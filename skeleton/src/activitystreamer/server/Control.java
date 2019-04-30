package activitystreamer.server;

import activitystreamer.msg.MSG;
import java.io.IOException;
import java.net.Socket;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import activitystreamer.util.Settings;

public class Control extends Thread {
	// control properties
	private static ArrayList<String> dead_list;
	private static ArrayList<Connection> connections;
	private static boolean term=false;
	private static Listener listener;
	protected static Control control = null;
	private static Map<String, Integer> peer_list;
	private static Map<Integer, String> msg_buff;
	private static ArrayList<String> queue;

	// server tags
	private static boolean isRoot = true;
	private static String server_id = ""; // server_id:server_port

	public static Control getInstance() {
		if(control==null){
			control=new Control();
		} 
		return control;
	}
	
	public Control() {
		// init the queue
		queue = new ArrayList<>();
		// initialize the connections array
		connections = new ArrayList<>();
		// initialize peer_list
		peer_list = new HashMap<>();
		//initialize dead_list
		dead_list = new ArrayList<>();
		// update self server ID as socket addr
		this.server_id = Settings.getLocalHostname() + ":" + Settings.getLocalPort();
		// start a listener
		try {
			listener = new Listener();
			this.initiateConnection();
			this.start();
		} catch (IOException e1) {
			System.exit(-1);
		}


	}

	// initial connect
	public void initiateConnection(){
		// make a connection to another server if remote hostname is supplied
		if(Settings.getRemoteHostname()!=null){
			try {
				this.isRoot = false;
				Connection c = outgoingConnection(new Socket(Settings.getRemoteHostname(),Settings.getRemotePort()));
				MSG m_io = new MSG(Settings.INITIAL_OUT, c.getSrcHost(), c.getSrcPort(), c.getDestHost(), c.getDestPort(), this.server_id);
				c.sendMsg(m_io.toSendString());
			} catch (IOException e) {
				System.out.println("Can't Connect to Remote");
			}
		}
	}

	/*
	 * Processing incoming messages from the connection.
	 * Return true if the connection should close.
	 */
	////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	public synchronized boolean process(Connection c_in,String m_in){
		MSG msg_recv = new MSG(m_in);
//		System.out.println(msg_recv.toSendString());
		if (msg_recv.getType().equals(Settings.INITIAL_OUT)){
			// other server init a connection to this server
			String remote_peer_id = msg_recv.getBody();
			// write id to connection id
			c_in.setConnId(remote_peer_id);
			// write entry to local peer list
			peer_list.put(remote_peer_id, 0);
			// reply with INITIAL_IN
			MSG m_ii = new MSG(Settings.INITIAL_IN, c_in.getSrcHost(), c_in.getSrcPort(), c_in.getDestHost(), c_in.getDestPort(), this.server_id);
			c_in.sendMsg(m_ii.toSendString());
			return false;
		}
		else
		if (msg_recv.getType().equals(Settings.INITIAL_IN)){
			// this server init a connection to other server and get reply
			String remote_peer_id = msg_recv.getBody();
			// write id to connection id
			c_in.setConnId(remote_peer_id);
			// write entry to local peer list
			peer_list.put(remote_peer_id, 0);
			return false;
		}
		else
		if (msg_recv.getType().equals(Settings.HEART_BEAT)){
			//continuously received heart_beat confirmation from other server--> necessary for error detection
			// clear local entry's counter
			String ent = msg_recv.getBody();
			peer_list.put(ent, 0);
			// forwarding current HB to other peers except the origin
			for(Connection conn : this.getConnections()){
				if (!conn.isEqual(c_in)) {
					// not send back
					MSG m_hb = new MSG(Settings.HEART_BEAT, conn.getSrcHost(), conn.getSrcPort(), conn.getDestHost(), conn.getDestPort(), ent);
					conn.sendMsg(m_hb.toSendString());
				}
			}
			return false;
		}
		else
		if (msg_recv.getType().equals(Settings.CLIENT_INIT)){
			// set connection id
			c_in.setConnId(msg_recv.getBody());
			// incomming client connection, reply with CLIENT_ACC
			MSG m_ca = new MSG(Settings.CLIENT_ACC, c_in.getSrcHost(), c_in.getSrcPort(), c_in.getDestHost(), c_in.getDestPort(), this.server_id);
			c_in.sendMsg(m_ca.toSendString());
			return false;
		}
		else
		if (msg_recv.getType().equals(Settings.CLIENT_MSG) || msg_recv.getType().equals(Settings.CLIENT_OUT)) {
			// A server connects to this server and sends a msg
			// put received msg to queue
			this.queue.add(msg_recv.getBody());
			// print out local queue
			if (this.queue.size() != 0) {
				for (String item : this.queue) {
					System.out.println(item);
				}
				System.out.println();
			}
			// forwarding CLIENT_OUT/CLIENT_MSG msg to other servers or clients, except for the origin
			for(Connection conn : this.getConnections()){
				// broadcast exclude the origin
				if (!conn.isEqual(c_in)){
					if (this.peer_list.containsKey(conn.getConnId())) {
						// forwarding to servers
						MSG m_cm = new MSG(Settings.CLIENT_MSG, conn.getSrcHost(), conn.getSrcPort(), conn.getDestHost(), conn.getDestPort(), msg_recv.getBody());
						conn.sendMsg(m_cm.toSendString());
					}
					else{
						// forwarding to connected clients
						MSG m_ci = new MSG(Settings.CLIENT_IN, conn.getSrcHost(), conn.getSrcPort(), conn.getDestHost(), conn.getDestPort(), msg_recv.getBody());
						conn.sendMsg(m_ci.toSendString());
					}
				}
			}
			return false;
		}

			// otherwise, close the connection
		return true;
	}
	////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	
	/*
	 * The connection has been closed by the other party.
	 */
	public synchronized void connectionClosed(Connection con){
		if(!term) connections.remove(con);
	}
	
	/*
	 * A new incoming connection has been established, and a reference is returned to it
	 */
	public synchronized Connection incomingConnection(Socket s) throws IOException{
//		log.debug("incomming connection: "+Settings.socketAddress(s));
		Connection c = new Connection(s);
		connections.add(c);
		return c;
		
	}
	
	/*
	 * A new outgoing connection has been established, and a reference is returned to it
	 */
	public synchronized Connection outgoingConnection(Socket s) throws IOException{
//		log.debug("outgoing connection: "+Settings.socketAddress(s));
		Connection c = new Connection(s);
		connections.add(c);
		return c;
	}
	
	@Override
	public void run(){
		System.out.println("Run Interval");
		while(!term){
			// do something with 5 second intervals in between
			try {
				Thread.sleep(Settings.getActivityInterval());
			}
			catch (InterruptedException e) {
				break;
			}
			if(!term){
				term=doActivity();
			}
			
		}
		// clean up
		for(Connection connection : connections){
			connection.closeCon();
		}
		listener.setTerm(true);
	}

	// do per interval
	public boolean doActivity(){
		if (this.getConnections().size() != 0){
			for(Connection c : this.getConnections()){
				MSG m_hb = new MSG(Settings.HEART_BEAT, c.getSrcHost(), c.getSrcPort(), c.getDestHost(), c.getDestPort(), this.server_id);
				c.sendMsg(m_hb.toSendString());
			}
		}
		else
			System.out.println("No Connection");
		// update local peer_list counter
		for(String ent : this.peer_list.keySet()){
			int val = this.peer_list.get(ent);
			val ++;
			this.peer_list.put(ent, val);
			System.out.println(ent + " = " + this.peer_list.get(ent));
			// update the dead_list, containing peer_id of dead peers
			if (val > Settings.DEAD_THRES){
				// dead peer_id saved
				this.dead_list.add(ent);
			}
			else {
				this.dead_list.remove(ent);
			}
		}
		// print out dead peer ids
		for(String dp : this.dead_list){
			this.peer_list.remove(dp);
			System.out.println("Dead Peer ID = " + dp);
		}
//		System.out.println();

		return false;
	}
	
	public final void setTerm(boolean t){
		term=t;
	}
	
	public final ArrayList<Connection> getConnections() {
		return connections;
	}
}

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
	private static ArrayList<Connection> connections;
	private static boolean term=false;
	private static Listener listener;
	protected static Control control = null;
	private static Map<String, Integer> peer_list;

	// server tags
	private static boolean isRoot = true;
	private static String server_id = "";

	public static Control getInstance() {
		if(control==null){
			control=new Control();
		} 
		return control;
	}
	
	public Control() {
		// initialize the connections array
		connections = new ArrayList<Connection>();
		// initialize peer_list
		peer_list = new HashMap<>();
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
	
	public void initiateConnection(){
		// make a connection to another server if remote hostname is supplied
		if(Settings.getRemoteHostname()!=null){
			try {
				isRoot = false;
				Connection c = outgoingConnection(new Socket(Settings.getRemoteHostname(),Settings.getRemotePort()));
				MSG m_io = new MSG(Settings.INITIAL_OUT, c.getSrcHost(), c.getSrcPort(), c.getDestHost(), c.getDestPort(), this.server_id);
				c.sendMsg(m_io.toSendString());
			} catch (IOException e) {
				System.out.println("Can't Connect to Remote");
//				System.exit(-1);
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
	public synchronized boolean process(Connection c,String m){
		MSG rm = new MSG(m);
		System.out.println(rm.toSendString());
		if (rm.getType().equals(Settings.INITIAL_OUT)){
			String remote_peer_id = rm.getBody();
			// write id to connection id
			c.setConnId(remote_peer_id);
			// write entry to local peer list
			peer_list.put(remote_peer_id, 0);
			// reply with INITIAL_IN
			MSG m_ii = new MSG(Settings.INITIAL_IN, c.getSrcHost(), c.getSrcPort(), c.getDestHost(), c.getDestPort(), this.server_id);
			c.sendMsg(m_ii.toSendString());
			return false;
		}
		else if (rm.getType().equals(Settings.INITIAL_IN)){
			String remote_peer_id = rm.getBody();
			// write id to connection id
			c.setConnId(remote_peer_id);
			// write entry to local peer list
			peer_list.put(remote_peer_id, 0);
			return false;
		}
		else if (rm.getType().equals(Settings.HEART_BEAT)){
			// clear local entry's counter
			String ent = rm.getBody();
			peer_list.put(ent, 0);
			// forwarding current HB to other peers except origin
			for(Connection conn : this.getConnections()){
				if (!c.isEqual(conn)) {
					// not send back
					MSG m_hb = new MSG(Settings.HEART_BEAT, c.getSrcHost(), c.getSrcPort(), c.getDestHost(), c.getDestPort(), ent);
					conn.sendMsg(m_hb.toSendString());
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
			} catch (InterruptedException e) {
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
	
	public boolean doActivity(){
//		System.out.println(	Settings.getLocalHostname() + " @ " + Settings.getLocalPort() + " -- Connection Counts: " + this.getConnections().size());
		if (this.getConnections().size() != 0){
			for(Connection c : this.getConnections()){
				MSG m_hb = new MSG(Settings.HEART_BEAT, c.getSrcHost(), c.getSrcPort(), c.getDestHost(), c.getDestPort(), this.server_id);
				c.sendMsg(m_hb.toSendString());
			}
		}
		else
			System.out.println("No Connection");
		for(String ent : this.peer_list.keySet()){
			// each entry self-increment
			int val = this.peer_list.get(ent);
			this.peer_list.put(ent, val + 1);
			System.out.println(ent + " = " + this.peer_list.get(ent));
		}
		System.out.println();
		return false;
	}
	
	public final void setTerm(boolean t){
		term=t;
	}
	
	public final ArrayList<Connection> getConnections() {
		return connections;
	}
}

package activitystreamer.client;

import activitystreamer.msg.MSG;
import activitystreamer.util.Settings;

import java.io.*;
import java.net.Socket;

public class ClientConnection extends Thread{
    private DataInputStream in;
    private DataOutputStream out;
    private BufferedReader inreader;
    private PrintWriter outwriter;

    private boolean open = false;
    private Socket s;
    private String lh;
    private int lp;
    private String rh;
    private int rp;
    private String client_id;


    public ClientConnection(String h, int p){
        this.rh = h;
        this.rp = p;
        try {
            s = new Socket(rh, rp);
            in = new DataInputStream(s.getInputStream());
            out = new DataOutputStream(s.getOutputStream());
            inreader = new BufferedReader( new InputStreamReader(in));
            outwriter = new PrintWriter(out, true);
            this.lh = s.getLocalAddress().toString().split("/")[1];
            this.lp = s.getLocalPort();
            this.client_id = this.lh + ":" + this.lp;
            this.initMsg();
            while (true) {
                MSG ca = new MSG(inreader.readLine());
                if (ca.getType().equals(Settings.CLIENT_ACC))
                    break;
            }
        }
        catch (Exception e)
        {
            System.out.println("Create Socket Failed");
            System.exit(1);
        }
        this.start();

    }

    private void initMsg(){
        if (this.getClientId() != null) {
            try {
                MSG ci = new MSG(Settings.CLIENT_INIT, this.lh, this.lp, this.rh, this.rp, this.getClientId());
                outwriter.println(ci.toSendString());
                outwriter.flush();
            } catch (Exception e) {
                System.out.println("Message Sending Error");
            }
        }
    }

    public void sendMsg(String msg) {
        try{
            MSG cm = new MSG(Settings.CLIENT_OUT, this.lh, this.lp, this.rh, this.rp, msg);
            outwriter.println(cm.toSendString());
            outwriter.flush();
//            System.out.println("Message Sent: " + msg);
            System.out.println("me: " + msg);
        }
        catch (Exception e){
            System.out.println("Message Sending Error");
        }
    }

    public String getClientId(){
        return this.client_id;
    }

    // receiving
    public void run(){
        try {
            while (true){
                String data = inreader.readLine();
                MSG rm = new MSG(data);
                // excluding the HEART_BEAT MSG from servers
//                if (!rm.getType().equals(Settings.HEART_BEAT)){
                if (rm.getType().equals(Settings.CLIENT_IN)){
                    System.out.println(rm.getBody());
                }
            }
        }
        catch (IOException e) {
            System.out.println("ClientConnection Exceptionally Closed");
        }
    }
}

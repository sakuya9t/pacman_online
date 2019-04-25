package activitystreamer.client;

import activitystreamer.msg.MSG;
import activitystreamer.util.Settings;

import java.io.*;
import java.net.Socket;

public class Client extends Thread{
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


    public Client(String h, String p){
        this.rh = h;
        this.rp = Integer.parseInt(p);
        try {
            s = new Socket(rh, rp);
            in = new DataInputStream(s.getInputStream());
            out = new DataOutputStream(s.getOutputStream());
            inreader = new BufferedReader( new InputStreamReader(in));
            outwriter = new PrintWriter(out, true);
            this.lh = s.getLocalAddress().toString().split("/")[1];
            this.lp = s.getLocalPort();
        }
        catch (Exception e)
        {
            System.out.println("Create Socket Failed");
        }
        this.start();
    }

    public void sendMsg(String msg) {
        try{
            MSG cm = new MSG(Settings.CLIENT_OUT, this.lh, this.lp, this.rh, this.rp, msg);
            outwriter.println(cm.toSendString());
            outwriter.flush();
            System.out.println("Message Sent: " + msg);

        }
        catch (Exception e){
            System.out.println("Message Sending Error");
        }
    }

    // receiving
    public void run(){
        try {
            while (true){
                String data = inreader.readLine();
                MSG rm = new MSG(data);
                if (!rm.getType().equals(Settings.HEART_BEAT)){
                    System.out.println("Client Received: " + data);
                }
            }

        }
        catch (IOException e) {
            System.out.println("Client Exceptionally Closed");
        }
    }
}

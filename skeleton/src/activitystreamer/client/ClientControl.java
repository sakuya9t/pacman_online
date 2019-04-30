package activitystreamer.client;

import activitystreamer.Client;

import java.util.Scanner;

public class ClientControl extends Thread{

    private String remote_ip;
    private int remote_port;
    private ClientConnection c;
    private int msg_cnt;

    public ClientControl(String ip, String port){
        this.remote_ip = ip;
        this.remote_port = Integer.parseInt(port);
        this.c = new ClientConnection(this.remote_ip, this.remote_port);
        this.msg_cnt = 0;
        this.start();
        activateSender();
    }

    private void activateSender(){
        if (this.c != null){
            Scanner scan = new Scanner(System.in);
            String sendData;
            while ((sendData = scan.nextLine()) != null){
                c.sendMsg(sendData);
            }
        }
    }

    public void run(){
        while (true){
            try {
                Thread.sleep(100);
                // do action per loop
                if(this.c != null){
                    c.sendMsg(c.getClientId() + " says " + this.msg_cnt);
                    this.msg_cnt ++;
                }
            }
            catch (Exception e){
                break;
            }
        }
    }
}

package activitystreamer.client;
import java.util.Scanner;

public class SimpleClient extends Thread {


    public static void main(String[] args){
		ClientControl c_ctr = new ClientControl(args[0], args[1]);
    }


}  
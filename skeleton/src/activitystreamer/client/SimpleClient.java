package activitystreamer.client;
import java.util.Scanner;

public class SimpleClient extends Thread {


    public static void main(String[] args) 
    {
		Client cli = new Client(args[0], args[1]);
		Scanner scan = new Scanner(System.in);
		String sendData;
		while ((sendData = scan.nextLine()) != null){
			cli.sendMsg(sendData);
		}
    }


}  
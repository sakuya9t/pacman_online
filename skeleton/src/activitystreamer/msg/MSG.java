package activitystreamer.msg;

public class MSG {
    private String type;
    private String src_host;
    private int src_port;
    private String dest_host;
    private int dest_port;
    private String body;

    // separate init
    public MSG(String t, String sh, int sp, String dh, int dp, String b){
        this.type = t;
        this.src_host = sh;
        this.src_port = sp;
        this.dest_host = dh;
        this.dest_port = dp;
        this.body = b;
    }

    // paring init
    public MSG(String s){
        String[] ss = s.split(";");
        this.type = ss[0];
        this.src_host = ss[1];
        this.src_port = Integer.parseInt(ss[2]);
        this.dest_host = ss[3];
        this.dest_port = Integer.parseInt(ss[4]);
        this.body = ss[5];
    }

    public String toSendString(){
        String res = this.type;
        res += ";" + this.src_host;
        res += ";" + this.src_port;
        res += ";" + this.dest_host;
        res += ";" + this.dest_port;
        res += ";" + this.body;
        return res;
    }

    // get message properties
    public String getType(){
        return this.type;
    }

    public String getSrcHost(){
        return this.src_host;
    }

    public int getSrcPort(){
        return this.src_port;
    }

    public String getDestHost(){
        return this.dest_host;
    }

    public int getDestPort(){
        return this.dest_port;
    }

    public String getBody(){
        return body;
    }
}

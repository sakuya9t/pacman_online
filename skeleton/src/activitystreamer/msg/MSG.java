package activitystreamer.msg;

public class MSG {
    private String type;
    private String src_host;
    private int src_port;
    private String dest_host;
    private int dest_port;
    private String body;

    public MSG(String t, String sh, int sp, String dh, int dp, String b){
        this.type = t;
        this.src_host = sh;
        this.src_port = sp;
        this.dest_host = dh;
        this.dest_port = dp;
        this.body = b;
    }

    public MSG(String s){
        String[] subs = s.split("||");
        this.type = subs[0];
        this.src_host = subs[1];
        this.src_port = Integer.parseInt(subs[2]);
        this.dest_host = subs[3];
        this.dest_port = Integer.parseInt(subs[4]);
    }

    public String toSendString(){
        String res = this.type.toString();
        res += "||" + this.src_host;
        res += "||" + this.src_port;
        res += "||" + this.dest_host;
        res += "||" + this.dest_port;
        res += "||" + this.body;
        return res;
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

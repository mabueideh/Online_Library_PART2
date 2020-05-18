import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.time.Duration;
import java.time.Instant;
import java.util.Random;

public class LookupTest {

	public static void main(String[] args) throws IOException {
		// TODO Auto-generated method stub

		String request = "http://192.168.1.107:5000/lookup/";
		long sum =0;
		long[] times = new long[10000];
		for(int i=1;i<=10000;i++) {
			Random r = new Random();
			int id = r.nextInt(7) + 1 ;
			String request_url = request + id;
			long time_ms = sendGET(request_url);
			if(i==1) times[i-1] = time_ms;
			else times[i-1] = time_ms + times[i-2];
		}
		System.out.println("Total time: " +times[9999]);
		System.out.println("Average time: " +times[9999]/10000.0);
		String out = "";
		for(int i=0;i<10000;i++) {
			if(i%1000 == 0) out= times[i] + "" + ','; 
		}
	    //BufferedWriter writer = new BufferedWriter(new FileWriter("c:/Users/Abueideh/Desktop/DOS Project/lookup_w_cache.csv"));
	    BufferedWriter writer = new BufferedWriter(new FileWriter("c:/Users/Abueideh/Desktop/DOS Project/lookup_n_cache.csv"));
	    writer.write(out);
	    writer.close();
		
	}
	
	private static long sendGET(String request_url) throws IOException {
		URL obj = new URL(request_url);
		HttpURLConnection con = (HttpURLConnection) obj.openConnection();
		con.setRequestMethod("GET");
		//start timer
		Instant start = Instant.now();
		int responseCode = con.getResponseCode();
		//stop timer
		Instant finish = Instant.now();
		long timeElapsed = Duration.between(start, finish).toMillis();
		System.out.println("GET Response Code : "+request_url+" : " + responseCode+" : " + timeElapsed);
		return timeElapsed;
	}
	
}

// Bloomberg components globally
import com.bloomberglp.blpapi.Event;
import com.bloomberglp.blpapi.Message;
import com.bloomberglp.blpapi.MessageIterator;
import com.bloomberglp.blpapi.Request;
import com.bloomberglp.blpapi.Element;
import com.bloomberglp.blpapi.Service;
import com.bloomberglp.blpapi.Session;
import com.bloomberglp.blpapi.SessionOptions;
import com.bloomberglp.blpapi.Name;
import com.bloomberglp.blpapi.Datetime;
// Java components globally
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

// The main class
public class GetDataNone
{
	// Constant for the Bloomberg API service to be used
	private static final String APIREFDATA_SVC = "//blp/refdata";

	// Main method
	public static void main(String[] args) throws Exception
  	{
    		GetDataNone example = new GetDataNone();
    		example.run();
    		System.out.println("Press ENTER to quit");
    		System.in.read();
  	}

	// Run method
	private void run() throws Exception
	{
		// Specify BB connection
		SessionOptions sessionOptions = new SessionOptions();
		sessionOptions.setServerHost("localhost");
		sessionOptions.setServerPort(8194);
		System.out.println("Connecting to " + sessionOptions.getServerHost()
           		 + ":" + sessionOptions.getServerPort());
		// Start BB session
    		Session session = new Session(sessionOptions);
		boolean sessionStarted = session.start();
		if (!sessionStarted)
		{
  			System.err.println("Failed to start session.");
  			return;
		}
		// Open the Service
		if (!session.openService(APIREFDATA_SVC))
		{
  			System.out.println("Failed to open service: " + APIREFDATA_SVC);
  			return;
		}
		Service refDataService = session.getService(APIREFDATA_SVC);

		///////////////////////////////////////////
		/* Construct and Send Request */
		///////////////////////////////////////////
		List<String[]> securitiesAndCurrencies = new ArrayList<>(Arrays.asList(
           	new String[]{"FB1", "CHF", "Comdty"},
            new String[]{"TU1", "USD", "Comdty"},
			new String[]{"FV1", "USD", "Comdty"},
			new String[]{"TY1", "USD", "Comdty"},
			new String[]{"WN1", "CHF", "Comdty"},
			new String[]{"CV1", "CAD", "Comdty"},
			new String[]{"XQ1", "CAD", "Comdty"},
			new String[]{"CN1", "CHF", "Comdty"},
			new String[]{"LGB1", "CAD", "Comdty"},
			new String[]{"WB1", "GBP", "Comdty"},
			new String[]{"WX1", "GBP", "Comdty"},
			new String[]{"G 1", "CHF", "Comdty"},
			new String[]{"UGL1", "GBP", "Comdty"},
			new String[]{"DU1", "CHF", "Comdty"},
			new String[]{"OE1", "CHF", "Comdty"},
			new String[]{"RX1", "CHF", "Comdty"},
			new String[]{"UB1", "EUR", "Comdty"},
			new String[]{"IK1", "EUR", "Comdty"},
			new String[]{"OAT1", "EUR", "Comdty"},
			new String[]{"XM1", "CHF", "Comdty"},
			new String[]{"JB1", "JPY", "Comdty"},
			new String[]{"KAA1", "KRW", "Comdty"},
			new String[]{"TFT1", "CHF", "Comdty"},
			new String[]{"SM1", "CHF", "Index"},
            new String[]{"ES1", "CHF", "Index"},
			new String[]{"PT1", "CHF", "Index"},
			new String[]{"VG1", "CHF", "Index"},
			new String[]{"Z 1", "CHF", "Index"},
			new String[]{"GX1", "CHF", "Index"},
			new String[]{"ST1", "CHF", "Index"},
			new String[]{"CF1", "CHF", "Index"},
			new String[]{"OI1", "CHF", "Index"},
			new String[]{"QC1", "CHF", "Index"},
			new String[]{"ATT1", "CHF", "Index"},
			new String[]{"BE1", "CHF", "Index"},
			new String[]{"EO1", "CHF", "Index"},
			new String[]{"OT1", "CHF", "Index"},
			new String[]{"XP1", "CHF", "Index"},
			new String[]{"TP1", "CHF", "Index"},
			new String[]{"NI1", "CHF", "Index"},
			new String[]{"HI1", "CHF", "Index"},
			new String[]{"IH1", "CHF", "Index"},
			new String[]{"MES1", "CHF", "Index"},
			new String[]{"BZ1", "CHF", "Index"},
			new String[]{"CL1", "CHF", "Comdty"},
            new String[]{"QS1", "CHF", "Comdty"},
			new String[]{"XB1", "CHF", "Comdty"},
			new String[]{"HO1", "CHF", "Comdty"},
			new String[]{"NG1", "CHF", "Comdty"},
			new String[]{"LMAHDS03 LME", "CHF", "Comdty"},
            new String[]{"LMCADS03", "CHF", "Comdty"},
			new String[]{"LMNIDS03", "CHF", "Comdty"},
			new String[]{"GC1", "CHF", "Comdty"},
			new String[]{"SI1", "CHF", "Comdty"},
			new String[]{"LC1", "CHF", "Comdty"},
            new String[]{"KC1", "CHF", "Comdty"},
			new String[]{"C 1", "CHF", "Comdty"},
			new String[]{"CT1", "CHF", "Comdty"},
			new String[]{"S 1", "CHF", "Comdty"},
			new String[]{"SB1", "CHF", "Comdty"},
            new String[]{"W 1", "CHF", "Comdty"}
        	));

		for (String[] pair : securitiesAndCurrencies) {
            String securityName1 = pair[0];
            String securityCurrency = pair[1];
			String securityName2 = pair[2];

			Request request = refDataService.createRequest("HistoricalDataRequest");
			request.append("securities", securityName1 + " N:02_0_N " + securityName2);

			request.append("fields", "PX_LAST");

			request.set("periodicitySelection", "DAILY");
			request.set("startDate", "19000101");
			request.set("endDate", "20231231");
			request.set("currency", securityCurrency);

			System.out.println("Sending Request: " + request);
			session.sendRequest(request, null);
			///////////////////////////////////////////

			// Handle Reply
			try (FileWriter writer = new FileWriter(securityName1 + "_" + securityName2 + "_" + securityCurrency + "NONE.csv")) {
				writer.write("name,date,PX_LAST\n"); // Write the header line
				// BASE start
				while (true) {
					Event event = session.nextEvent();
					MessageIterator msgIter = event.messageIterator();
					while (msgIter.hasNext()) {
	      					Message msg = msgIter.next();
						if (msg.messageType().toString().equals("HistoricalDataResponse")) {
                       					parseAndWriteCSV(writer, msg);
                    				}
	      					else {System.out.println(msg);}
					}
					if (event.eventType() == Event.EventType.RESPONSE) {
						break;
					}
				}
				// BASE end
			} catch (IOException e) {
           			e.printStackTrace();
        		}
		}
	}

	private void parseAndWriteCSV(FileWriter writer, Message msg) throws IOException {
        Element securityDataArray = msg.getElement("securityData");
		String name = securityDataArray.getElementAsString("security");
           	Element fieldDataArray = securityDataArray.getElement("fieldData");
           	for (int j = 0; j < fieldDataArray.numValues(); ++j) {
               	Element fieldData = fieldDataArray.getValueAsElement(j);
               	String date = fieldData.getElementAsString("date");
               	double pxLast = fieldData.getElementAsFloat64("PX_LAST");
               	// Write to CSV
               	writer.write(name + "," + date + "," + pxLast + "\n");
        }
		System.out.println("Success");
    }

}

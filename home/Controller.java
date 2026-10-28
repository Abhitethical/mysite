@RestController
@CrossOrigin
public class VerifyController {

    @PostMapping("/verify-pan")
    public Map<String, String> verifyPan(@RequestBody Map<String, String> req) {

        String pan = req.get("pan");
        String name = req.get("name");

        // CALL REAL API HERE (example placeholder)
        boolean isValid = callPanApi(pan);

        Map<String, String> res = new HashMap<>();

        if (isValid) {
            res.put("message", "PAN Verified Successfully");
        } else {
            res.put("message", "Invalid PAN");
        }

        return res;
    }

    private boolean callPanApi(String pan) {

        // Example: You would call:
        // NSDL / Karza / Signzy API using RestTemplate or WebClient

        return pan.matches("[A-Z]{5}[0-9]{4}[A-Z]");
    }
}
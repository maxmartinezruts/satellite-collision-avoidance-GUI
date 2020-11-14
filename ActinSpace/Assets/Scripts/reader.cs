using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEditor;
using System.IO;

public class reader : MonoBehaviour
{


    
    public LineRenderer orbit;

    public GameObject spotLight;

    public string code;

    public Text eccentricity_val;
    public Text inclination_val;
    public Text RAAN_val;

    public Text perigee_argument_val;
    public Text mean_anomaly_val;
    public Text mean_motion_val;

    public Text code_val;
    public Text orbit_val;
    public Text title_val;

    public Text x_val;
    public Text y_val;
    public Text z_val;
    public Text vx_val;
    public Text vy_val;
    public Text vz_val;

    public Text type_val;
    public Text status_val;

    List<Vector3> orbit_points = new List<Vector3>();
    List<GameObject> collisions = new List<GameObject>();

    public GameObject coll;


    Dictionary<string, Satellite> code_to_sat =
        new Dictionary<string, Satellite>();    // Start is called before the first frame update

    public GameObject ball;
    void Start()
    {
        StreamReader rdr;

        rdr = new StreamReader("Assets/Resources/parameters.csv");    // Read the text from directly from the test.txt file
        int j = 0;                              // Initialize j to 0 (j is the counter of waypoints)
        bool readCSV = false;                   // While not finished reading      
        
        while (j<1000){ 
            
            string line = rdr.ReadLine();    // Read next line
            if (line == null ){                 // If line is empty STOP reading
                readCSV = true;             
            }else{
                string[] parts_of_line = line.Split(',');           // Split line in columns
                for ( int i = 0; i < parts_of_line.Length; i++ ){   // For each column
                    parts_of_line[i] = parts_of_line[i].Trim();     // Remove spaces 
                    // print(parts_of_line[i].Trim());           // Add to table


                }   
                j+=1;                                               // Add 1 to counter 

                if (parts_of_line[1] != "nan"){
                    
                    float x = float.Parse(parts_of_line[0]);
                    float y = float.Parse(parts_of_line[1]);
                    float z = float.Parse(parts_of_line[2]);
                    float vx = float.Parse(parts_of_line[3]);
                    float vy = float.Parse(parts_of_line[4]);
                    float vz = float.Parse(parts_of_line[5]);
                    string code = parts_of_line[6];
                    string eccentricity = parts_of_line[7];
                    string inclination = parts_of_line[8];
                    string RAAN = parts_of_line[9];
                    string perigee_argument = parts_of_line[10];
                    string mean_anomaly = parts_of_line[11];
                    string mean_motion = parts_of_line[12];
                    string title = parts_of_line[13];
                    string orbit = parts_of_line[14];
                    string status = parts_of_line[15];
                    string type = parts_of_line[16];

                    Vector3 position = new Vector3(x/100000,y/100000,z/100000);   
                    Vector3 velocity = new Vector3(vx,vy,vz);   

                    GameObject newBall = Instantiate(ball);                                                   // Create new sphere representing a waypoint
                    newBall.transform.position = position;

                    Satellite newSatellite = new Satellite(position, velocity, code, eccentricity,inclination, RAAN, perigee_argument, mean_anomaly, mean_motion, title, orbit, newBall, type, status);
                    code_to_sat.Add(code, newSatellite);

                }
            }
        }
        
        rdr.Close();                                     // Close file after finish reading

        StartCoroutine(Countdown());
                StartCoroutine(Countdown_2());

        
    }

    // Update is called once per frame
    void Update()
    {
        if (code_to_sat.ContainsKey(code)){
            title_val.text = code_to_sat[code].title;
            eccentricity_val.text = code_to_sat[code].eccentricity + " [-]";
            inclination_val.text = code_to_sat[code].inclination + " [deg]";
            RAAN_val.text = code_to_sat[code].RAAN + " [deg]";
            perigee_argument_val.text = code_to_sat[code].perigee_argument + " [deg]";

            mean_anomaly_val.text = code_to_sat[code].mean_anomaly + " [deg]";
            mean_motion_val.text = code_to_sat[code].mean_motion + " [rev/day]";
            orbit_val.text = code_to_sat[code].orbit;
            code_val.text = code;
            x_val.text = code_to_sat[code].position.x.ToString() + "[km]";
            y_val.text = code_to_sat[code].position.y.ToString() + " [km]";
            z_val.text = code_to_sat[code].position.z.ToString() + " [km]";
            vx_val.text = code_to_sat[code].velocity.x.ToString() + " [km/s]";
            vy_val.text = code_to_sat[code].velocity.y.ToString() + " [km/s]";
            vz_val.text = code_to_sat[code].velocity.z.ToString() + " [km/s]";
            status_val.text = code_to_sat[code].status;
            type_val.text = code_to_sat[code].type;




            // code_to_sat[code].obj.transform.localScale = new Vector3(10,10,10);
            spotLight.transform.position = code_to_sat[code].position;
        }


    }

     IEnumerator Countdown () {

        while (true) {
                            DoStuff ();

            yield return new WaitForSeconds (0.2f);
        }
    }

     IEnumerator Countdown_2 () {

        while (true) {
                            updateCollisions ();

            yield return new WaitForSeconds (2f);
        }
    }

    void DoStuff(){
        print("fsdfs");
        NewQuery();
        updateProjection();
    }

    public void updateCollisions(){
         GameObject[] gameObjects;
        gameObjects = GameObject.FindGameObjectsWithTag ("collision");
     
     for(var i = 0 ; i < gameObjects.Length ; i ++)
     {
         Destroy(gameObjects[i]);
     }
         StreamReader rdr_collisions;
        try{
                    bool readCSV;

            rdr_collisions = new StreamReader("Assets/Resources/collisions.csv");    // Read the text from directly from the test.txt file

            readCSV = false;                   // While not finished reading      
            int j = 0;
            while (!readCSV && j <4){ 
                
                string line = rdr_collisions.ReadLine();    // Read next line
                if (line == null ){                 // If line is empty STOP reading
                    readCSV = true;             
                }else{
                    string[] parts_of_line = line.Split(',');           // Split line in columns
                    for ( int i = 0; i < parts_of_line.Length; i++ ){   // For each column
                        parts_of_line[i] = parts_of_line[i].Trim();     // Remove spaces 
                    }   
                    if (parts_of_line[1] != "nan"){
                        string title = parts_of_line[0];
                        string code = parts_of_line[1];
                        string date = parts_of_line[2];


                        GameObject newCollision = Instantiate (coll) as GameObject;
                        newCollision.SetActive(true);
                        newCollision.transform.parent = coll.transform.parent;
                        j += 1;
                        newCollision.GetComponent<RectTransform>().localPosition = new Vector3(0,280-110*j,0);
                        newCollision.transform.Find("title").GetComponent<Text>().text = title;
                        newCollision.transform.Find("code").GetComponent<Text>().text = code;
                        newCollision.transform.Find("date").GetComponent<Text>().text = date;

                        newCollision.tag = "collision";
                        print("fdsffsdfss");

                        collisions.Add(newCollision);
                    }
                }
            }

            rdr_collisions.Close();                                     // Close file after finish reading

        }
        catch (IOException  e)

        {
            print("Could not read collisions");
        }


    }

    public void NewQuery(){
 
        if (code_to_sat.ContainsKey(code)){
            StreamWriter writer = new StreamWriter("Assets/Resources/query.csv"); 
    
            writer.WriteLine(code);
            writer.WriteLine("01/07/2020  04:00:00");
            writer.WriteLine("01/07/2020  09:00:00");
            writer.Close();
        }

    }

    public void updateProjection(){
                orbit_points = new List<Vector3>();

        StreamReader rdr_projection;
        try{
                    bool readCSV;

            rdr_projection = new StreamReader("Assets/Resources/project.csv");    // Read the text from directly from the test.txt file

            readCSV = false;                   // While not finished reading      
            
            while (!readCSV){ 
                
                string line = rdr_projection.ReadLine();    // Read next line
                if (line == null ){                 // If line is empty STOP reading
                    readCSV = true;             
                }else{
                    string[] parts_of_line = line.Split(',');           // Split line in columns
                    for ( int i = 0; i < parts_of_line.Length; i++ ){   // For each column
                        parts_of_line[i] = parts_of_line[i].Trim();     // Remove spaces 
                    }   
                    if (parts_of_line[1] != "nan"){
                        float x = float.Parse(parts_of_line[0]);
                        float y = float.Parse(parts_of_line[1]);
                        float z = float.Parse(parts_of_line[2]);
                        Vector3 position = new Vector3(x/100000,y/100000,z/100000);   
                        orbit_points.Add(position);
                    }
                }
            }
            

            rdr_projection.Close();                                     // Close file after finish reading

            orbit.positionCount = orbit_points.Count;              // Number of points of the line that defines the path
            for (int i =0; i< orbit_points.Count; i++){
                orbit.SetPosition(i, orbit_points[i]);    // Create a new pivot in line renderer         
            }   
        }
        catch (IOException  e)

        {
            print("Could not read");
        }

    }
}

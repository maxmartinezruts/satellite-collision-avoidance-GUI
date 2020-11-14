using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Satellite         // Satellite class
{
    public Vector3 position;
    public Vector3 velocity;
    public string code;
    public string eccentricity;
    public string RAAN;
    public string inclination;
    public string perigee_argument;
    public string mean_anomaly;
    public string mean_motion;
    public string title;
    public string orbit;
    public string type;
    public string status;
    public GameObject obj;


    public Satellite(Vector3 _position, Vector3 _velocity, string _code, string _eccentricity, string _inclination, string _RAAN, string _perigee_argument, string _mean_anomaly, string _mean_motion, string _title, string _orbit, GameObject _obj, string _type, string _status)
        {
            position = _position;
            velocity = _velocity;
            code = _code;
            eccentricity = _eccentricity;
            inclination = _inclination;
            RAAN = _RAAN;
            perigee_argument = _perigee_argument;
            mean_anomaly = _mean_anomaly;
            mean_motion = _mean_motion;
            title = _title;
            orbit = _orbit;
            obj = _obj;
            type = _type;
            status = _status;


        }
}

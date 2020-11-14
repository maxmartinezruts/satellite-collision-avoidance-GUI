using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class GUIController : MonoBehaviour
{

    public GameObject camera;

    public Vector3 posCameraMain;
    public Vector3 posCameraInfo;

        public Vector3 posCameraDanger;


    public GameObject back;

    public GameObject infoSat;
    public GameObject evaluateRisk;
    public GameObject inputOrbit;

    public GameObject satCode;
    public GameObject satInfo;

    public GameObject collisionInfo;

    public GameObject go;

    Vector3 targetCamera;
    // Start is called before the first frame update
    void Start()
    {
        MainScene();
    }

    // Update is called once per frame
    void Update()
    {
        camera.transform.position = Vector3.Lerp(camera.transform.position, targetCamera, 0.1f);
    }

    public void InfoScene(){
        targetCamera = posCameraInfo;
        back.SetActive(true);
        
        infoSat.SetActive(true);
        evaluateRisk.SetActive(false);
        inputOrbit.SetActive(false);
        satCode.SetActive(true);
        satInfo.SetActive(true);
        // go.SetActive(true);
        collisionInfo.SetActive(false);
    }
    public void MainScene(){
        targetCamera = posCameraMain;
        back.SetActive(false);

        infoSat.SetActive(true);
        evaluateRisk.SetActive(true);    
        inputOrbit.SetActive(true);

        satCode.SetActive(false);
        satInfo.SetActive(false);
        go.SetActive(false);
        collisionInfo.SetActive(false);

    }

    public void checkCollision(){
        targetCamera = posCameraDanger;
        back.SetActive(true);
        satCode.SetActive(true);

        infoSat.SetActive(false);
        evaluateRisk.SetActive(true);    
        inputOrbit.SetActive(false);

        satInfo.SetActive(false);
        go.SetActive(false);
        collisionInfo.SetActive(true);
    }

    public void SearchSat(int satCode){


    }
}

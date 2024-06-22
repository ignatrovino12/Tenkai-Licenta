// IMPORTS


//DATA

interface Waypoint_upload {
  lat: number;
  lng: number;
  ele: number;
  time: number;
}

//FUNCTIONS
function find_closest_waypoint(time: number, waypoints: Waypoint_upload[]): [Waypoint_upload,number] {
    time = time + waypoints[0].time
    let closestWaypoint = waypoints[0];
    let closestIndex = 0;
    let lastIndex =0;
    let closestTimeDiff = waypoints[0].time;
    
    for (let i = 1; i < waypoints.length; i++) {

        if(time<=waypoints[i].time) {
            const timeDiff = waypoints[i].time - time;
            
            if (timeDiff < closestTimeDiff) {
                closestWaypoint = waypoints[i];
                closestTimeDiff = timeDiff;
                closestIndex = i;
            }

        }

        // if time is not synchronized well till the end, make the waypoint stay at end
        else if (time>waypoints[waypoints.length-1].time){
            closestWaypoint=waypoints[waypoints.length-1];
            closestIndex=waypoints.length-1;
        }

    }                                                                              
                                                                                                                      
    if (closestIndex>0) {lastIndex=closestIndex-1}
    else {lastIndex=closestIndex}
    return [closestWaypoint,lastIndex];
}

async function update_map(waypoint: Waypoint_upload, map: any, lastWaypoint: Waypoint_upload, time : number, speed:number, zerowaypoint: Waypoint_upload): Promise<number> {
    return new Promise<number>((resolve, reject) => {
        if (typeof window !== "undefined") {
            import("leaflet").then(L => {
                if (map && waypoint) {
                    if (map.currentMarker) {
                        map.removeLayer(map.currentMarker);
                    }

                    if ( (waypoint === lastWaypoint) || (waypoint.time < lastWaypoint.time) ) {
                        const newMarker = L.marker([waypoint.lat, waypoint.lng]).addTo(map);
                        map.currentMarker = newMarker;
                        resolve(speed);
                    } else {
                        const startTime = zerowaypoint.time; 
                        const absoluteCurrentTime = startTime + time;
                        const timeDifference = waypoint.time - lastWaypoint.time;

                        const distance = Math.sqrt(Math.pow(waypoint.lat - lastWaypoint.lat, 2) + Math.pow(waypoint.lng - lastWaypoint.lng, 2));     

                        let ratio = (absoluteCurrentTime - lastWaypoint.time) / timeDifference;
                        ratio = Math.max(0, Math.min(1, ratio)); //ratio in [0,1], otherwise can be out of bounds 

                        const currentLat = lastWaypoint.lat + (waypoint.lat - lastWaypoint.lat) * ratio;
                        const currentLng = lastWaypoint.lng + (waypoint.lng - lastWaypoint.lng) * ratio;

                        const newMarker = L.marker([currentLat, currentLng]).addTo(map);
                        map.currentMarker = newMarker;
                        
                        // calculate speed
                        const distanceInKm = distance * 111.1; // convert distance degrees to km
                        const timeDifferenceInHours = timeDifference / 3600;
                        const new_speed = parseFloat((distanceInKm / timeDifferenceInHours).toFixed(2));
                        resolve(new_speed);
                    }
                }
            }).catch(error => {
                reject(error);
            });
        }
    });
}



//   EXPORTS
export { find_closest_waypoint, update_map }
export type { Waypoint_upload  }


// IMPORTS


//DATA

interface Waypoint_upload {
  lat: number;
  lng: number;
  ele: number;
  time: number;
}

//FUNCTIONS
function find_closest_waypoint(time: number, waypoints: Waypoint_upload[]): Waypoint_upload {
    time = time + waypoints[0].time
    let closestWaypoint = waypoints[0];
    let closestTimeDiff = Math.abs(waypoints[0].time - time);
    for (let i = 1; i < waypoints.length; i++) {
        const timeDiff = Math.abs(waypoints[i].time - time);
        
        if (timeDiff < closestTimeDiff) {
            closestWaypoint = waypoints[i];
            closestTimeDiff = timeDiff;
        }
    }
    return closestWaypoint;
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

                        const ratio = (absoluteCurrentTime - lastWaypoint.time) / timeDifference;

                        const currentLat = lastWaypoint.lat + (waypoint.lat - lastWaypoint.lat) * ratio;
                        const currentLng = lastWaypoint.lng + (waypoint.lng - lastWaypoint.lng) * ratio;

                        const newMarker = L.marker([currentLat, currentLng]).addTo(map);
                        map.currentMarker = newMarker;
                        
                        // calculate speed
                        const distanceInKm = distance * 111.32; // convert distance degrees to km
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


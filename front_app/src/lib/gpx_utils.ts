
interface Waypoint_upload {
  lat: number;
  lng: number;
  ele: number;
  time: number;
}

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

function update_map(waypoint: Waypoint_upload, map: any) {
    if (typeof window !== "undefined") {
        
        import("leaflet").then(L => {
            if (map && waypoint) {
                const waypointKey = waypoint.time.toString();
    
                if (map.currentMarker) {
                    map.removeLayer(map.currentMarker);
                }
                const newMarker = L.marker([waypoint.lat, waypoint.lng]).addTo(map);
                map.currentMarker = newMarker;
            }
        });
    }
}



//   EXPORTS
export { update_map}
export { find_closest_waypoint }
export type { Waypoint_upload  }


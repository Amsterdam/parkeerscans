package main

var dbColumns = []string{
	"scan_id",         //  ScanId;
	"scan_moment",     //  scnMoment;
	"device_id",       //  device id
	"scan_source",     //  scan_source;
	"longitude",       //  scnLongitude;
	"latitude",        //  scnLatitude;
	"buurtcode",       //  buurtcode;
	"afstand",         //  aftand to pvak?
	"sperscode",       //  spersCode;
	"qualcode",        //  qualCode;
	"ff_df",           //  FF_DF;
	"nha_nr",          //  NHA_nr;
	"nha_hoogte",      //  NHA_hoogte;
	"uitval_nachtrun", //  uitval_nachtrun;

	// new since 10-2017
	"parkingbay_distance",  //  DistanceToParkingBay;
	"gps_vehicle",          //  GPS_Vehicle;
	"gps_plate",            //  GPS_PLate;
	"gps_scandevice",       //  GPS_ScanDevice;
	"location_parking_bay", //  location_ParkingBay;
	"parkingbay_angle",     //  ParkingBay_angle;
	"reliability_gps",      //  Reliability_GPS
	"reliability_ANPR",     //  Reliability_ANPR

	// extra fields
	"stadsdeel",       //  stadsdeel;
	"buurtcombinatie", //  buurtcombinatie;
	"geometrie",       //  geometrie

}

var columns22 = []string{
	"scan_id",         //  ScanId;
	"scan_moment",     //  scnMoment;
	"device_id",       //  device id
	"scan_source",     //  scan_source;
	"longitude",       //  scnLongitude;
	"latitude",        //  scnLatitude;
	"buurtcode",       //  buurtcode;
	"afstand",         //  aftand to pvak?
	"sperscode",       //  spersCode;
	"qualcode",        //  qualCode;
	"ff_df",           //  FF_DF;
	"nha_nr",          //  NHA_nr;
	"nha_hoogte",      //  NHA_hoogte;
	"uitval_nachtrun", //  uitval_nachtrun;

	// new since 10-2017
	"parkingbay_distance",  //  DistanceToParkingBay;
	"gps_vehicle",          //  GPS_Vehicle;
	"gps_plate",            //  GPS_PLate;
	"gps_scandevice",       //  GPS_ScanDevice;
	"location_parking_bay", //  location_ParkingBay;
	"parkingbay_angle",     //  ParkingBay_angle;
	"reliability_gps",      //  Reliability_GPS
	"reliability_ANPR",     //  Reliability_ANPR

	// extra fields
	"stadsdeel",       //  stadsdeel;
	"buurtcombinatie", //  buurtcombinatie;
	"geometrie",       //  geometrie

}

var columns23 = []string{
	"scan_id",         //  ScanId;
	"scan_moment",     //  scnMoment;
	"device_id",       //  device id
	"scan_source",     //  scan_source;
	"longitude",       //  scnLongitude;
	"latitude",        //  scnLatitude;
	"buurtcode",       //  buurtcode;
	"scan_message",    //  'scan_message'
	"sperscode",       //  spersCode;
	"qualcode",        //  qualCode;
	"ff_df",           //  FF_DF;
	"nha_nr",          //  NHA_nr;
	"nha_hoogte",      //  NHA_hoogte;
	"uitval_nachtrun", //  uitval_nachtrun;

	// new since 10-2017
	"parkingbay_distance",  //  DistanceToParkingBay;
	"gps_vehicle",          //  GPS_Vehicle;
	"gps_plate",            //  GPS_PLate;
	"gps_scandevice",       //  GPS_ScanDevice;
	"location_parking_bay", //  location_ParkingBay;
	"parkingbay_angle",     //  ParkingBay_angle;
	"reliability_gps",      //  Reliability_GPS
	"reliability_ANPR",     //  Reliability_ANPR
	"DevCode",              //  Devicecode

	// extra fields
	"stadsdeel",       //  stadsdeel;
	"buurtcombinatie", //  buurtcombinatie;
	"geometrie",       //  geometrie
}

func makeIndexMapping(columns []string) map[string]int {

	idxMap := make(map[string]int)
	// fill map
	for i, field := range columns {
		idxMap[field] = i
	}
	return idxMap
}

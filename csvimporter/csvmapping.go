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

	// new since 3-2018
	"parkeerrecht_id", //  ParkeerrechtId
	// extra fields
	"stadsdeel",       //  stadsdeel;
	"buurtcombinatie", //  buurtcombinatie;
	"geometrie",       //  geometrie

}

var columns2016 = []string{
	"scan_id",         //  ScanId;
	"scan_moment",     //  scnMoment;
	"device_id",       //  device id
	"scan_source",     //  scan_source;
	"longitude",       //  scnLongitude;
	"latitude",        //  scnLatitude;
	"buurtcode",       //  buurtcode;
	"afstandX",        //  afstand to pvak?  DISABELED
	"sperscode",       //  spersCode;
	"qualcode",        //  qualCode;
	"ff_df",           //  FF_DF;
	"nha_nr",          //  NHA_nr;
	"nha_hoogte",      //  NHA_hoogte;
	"uitval_nachtrun", //  uitval_nachtrun;

	// extra fields
	"stadsdeel",       //  stadsdeel;
	"buurtcombinatie", //  buurtcombinatie;
	"geometrie",       //  geometrie

}

// 01 ScanId;
// 02 scnMoment;
// 03 device_id;
// 04 scan_source;
// 05 scnLongitude;
// 06 scnLatitude;
// 07 buurtcode;
// 08 afstand;
// 09 spersCode;
// 01 qualCode;
// 11 FF_DF;
// 12 NHA_nr;
// 13 NHA_hoogte;
// 14 uitval_nachtrun;
// 15 DistanceToParkingBay;
// 16 GPS_Vehicle;
// 17 GPS_PLate;
// 18 GPS_ScanDevice;
// 19 location_ParkingBay;
// 20 ParkingBay_angle;
// 21 Reliability_GPS;
// 22 Reliability_ANPR

var columns22 = []string{
	"scan_id",         //  ScanId;
	"scan_moment",     //  scnMoment;
	"device_id",       //  device_id
	"scan_source",     //  scan_source;
	"longitude",       //  scnLongitude;
	"latitude",        //  scnLatitude;
	"buurtcode",       //  buurtcode;
	"afstandX",        //  afstand to pvak?  !! DISABELED
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
	"device_code",          //  Devicecode

	// extra fields
	"stadsdeel",       //  stadsdeel;
	"buurtcombinatie", //  buurtcombinatie;
	"geometrie",       //  geometrie
}

var columns24 = []string{
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
	"device_code",          //  Devicecode

	// new since 10-2018
	"parkeerrecht_id", //  ParkeerrechtId

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

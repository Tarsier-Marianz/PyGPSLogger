# -*- coding: utf-8 -*-
"""
Created on Sun Nov  8 11:32:12 2015

Class to parse GPS NMEA data from the Adifruit GPS logger

@author: Steve
"""

import math
from pynmea import nmea

class ParseNmea:
    """ 
    A class to read in a NMEA csv data file and parse into
    something a little easier to handle.
    
    Format of parsed data is:
        0: Timestamp (HHmmss.mmm)
        1: latitude
        2: longitude
        3: altitude
        4: distance (m)
        5: number of satellites
        6: gps quality
        7: speed (knots)
        8: course
        9: datestamp (DDMMYY)
    """
    
    def __init__(self):  
        self.gpsData = []  # instance variable unique to each instance
    
    def ParseGpsNmeaFile(self, filename):
        """
        Read in a GPS NMEA formated input file <filename>
        Parse it assuming the file contains pairs of GPGGA and GPRMC lines
          of data. Some fault tolerance if one or the other line is dropped or
          the line is poorly formed/corrupt.
        Return the array of data for subsequent parsing
        """
        print( "Parsing input NMEA file %s" % filename)
        self.gpsData = []
    
        gprmc = nmea.GPRMC()
        gpgga = nmea.GPGGA()
    
        outputLine = ""
        lastLat = 0.0
        lastLon = 0.0
        
        for line in open(filename,'r'):
    
            # strip any whitespace from edges
            line = line.strip()
            if not line:
                continue
    
            # Try to catch corrupt lines early
            if not line.startswith('$GP'):
                print( 'Bad line: ', line)
                continue
    
            # Skip any sentence other than GPGGA
            if line.startswith('$GPGGA'):
                outputLine = ""
                gpgga.parse(line)
                if self.DoNotHaveFix(gpgga.latitude):
                    continue
                [lat, lon] = self.ConvertLatLonToDecimalDegrees(
                    gpgga.latitude,
                    gpgga.lat_direction,
                    gpgga.longitude,
                    gpgga.lon_direction)
                distance = self.HaversineDistance(lat,lastLat,lon,lastLon)
                lastLat = lat
                lastLon = lon
                outputLine = "%s,%f,%f,%s,%f,%s,%s," % \
                    (gpgga.timestamp, lat, lon, gpgga.antenna_altitude, distance, \
                    gpgga.num_sats, gpgga.gps_qual)
            elif line.startswith('$GPRMC'):
                if(len(outputLine)==0):
                    continue
                gprmc.parse(line)
                outputLine += "%s,%s,%s" % \
                    (gprmc.spd_over_grnd, gprmc.true_course, gprmc.datestamp)
                self.gpsData.append(outputLine)
                outputLine = ""
        
    def ParseGpsNmeaGprmcFile(self, filename):
        """
        Read in a GPS NMEA formated input file <filename>
        Parse it assuming the file contains only GPRMC lines of data. 
        Some fault tolerance if one or the other line is dropped or
          the line is poorly formed/corrupt.
        Return the array of data for subsequent parsing
        """
        print( "Parsing input NMEA file %s" % filename)
    
        gprmc = nmea.GPRMC()
    
        outputLine = ""
        lastLat = 0.0
        lastLon = 0.0
        for line in open(filename,'r'):
    
            # strip any whitespace from edges
            line = line.strip()
            if not line:
                continue
    
            # Try to catch corrupt lines early
            if not line.startswith('$GP'):
                print ('Bad line: ', line)
                continue
    
            # Skip any sentence other than GPGGA
            if line.startswith('$GPRMC'):
                outputLine = ""
                gprmc.parse(line)
                if self.DoNotHaveFix(gprmc.lat):
                    continue
                [lat, lon] = self.ConvertLatLonToDecimalDegrees(gprmc.lat,
                    gprmc.lat_dir,
                    gprmc.lon,
                    gprmc.lon_dir)
                distance = self.HaversineDistance(lat,lastLat,lon,lastLon)
                lastLat = lat
                lastLon = lon
                outputLine = "%s,%f,%f,0,%f,1?,?," % \
                    (gprmc.timestamp, lat, lon, distance)
                outputLine += "%s,%s,%s" % \
                    (gprmc.spd_over_grnd, gprmc.true_course, gprmc.datestamp)
                self.gpsData.append(outputLine)
    
    def SaveReducedGpsData(self, filename):
        """
        Save the parsed GPS data to <filename>
        """
        print( "Saving GPS data to %s" % filename)
    
        csv_file = open(filename,'w')
        csv_file.write("#Timestamp,lat,lon,alt,dist (m),num sats,gps qual,speed (knts),course,date\n")
        for line in self.gpsData:
            csv_file.write(line + "\n")
        csv_file.close()
        
    def DoNotHaveFix(self, latitude):
        """
        Check to make sure the lat is populated, indicating have satelites
        fix
        """
        if len(latitude) == 0:
            return True
        else:
            return False
        
    def ConvertLatLonToDecimalDegrees(self, latitude,lat_direction,longitude,lon_direction):
        """
        The adafruit gps sheild writes lat and lon in the format DDMM.MMMM and
        DDDMM.MMMM. Also the cardinal directions N,S,E,W translate to +,-,+,- as
        far as Google is concerned.
        """
        latDegrees = int(latitude[0:2])
        latMinutes = float(latitude[2:])
        latitude = latDegrees + latMinutes/60.0
    
        if lat_direction == 'S':
            latitude = -1.0 * latitude
    
        longDegrees = int(longitude[0:3])
        longMinutes = float(longitude[3:])
        longitude = longDegrees + longMinutes/60.0
    
        if lon_direction == 'W':
            longitude = -1.0 * longitude
    
        return [latitude, longitude]

    def HaversineDistance(self, lat_1, lat_2, lon_1, lon_2):
        """
        Use the haversine formula to calculate distance between two locations.
        Latitudes and Longitudes need to be in decimal degrees.
        a = sin^2(deltaPhi/2) + cos(phi_1)*cos(phi_2)*sin^2(deltaLambda/2)
        c = 2*atan2(sqrt(a),sqrt(1-a))
        distance = RadiusOfEarth*c
        """
        RadiusOfEarth = 6371000.0 # meters
        phi_1 = math.radians(lat_1)
        phi_2 = math.radians(lat_2)
        deltaPhi = math.radians(lat_2-lat_1)
        deltaLambda = math.radians(lon_2-lon_1)
        sinDeltaPhiSqrd = math.sin(deltaPhi/2.)*math.sin(deltaPhi/2)
        cosPhi1CosPhi2 = math.cos(phi_1)*math.cos(phi_2)
        sinDeltaLambdaSqrd = math.sin(deltaLambda/2.)*math.sin(deltaLambda/2)
        a = sinDeltaPhiSqrd + cosPhi1CosPhi2*sinDeltaLambdaSqrd
        c = 2.0*math.atan2(math.sqrt(a),math.sqrt(1-a))
        distance = RadiusOfEarth*c
        if distance > 1000.0:
            distance = 0.0
        return distance

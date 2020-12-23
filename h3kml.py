#!/usr/bin/env python3
"""
Very simple HTTP server in python for logging requests
Usage::
    ./h3kml.py [<port>]
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
#import cgi
import logging
import simplekml
import h3


def geth3polys(lat,lng,alt):
    # i'm sure there is a much more elegant way to do this
    # i assume these are meters so this may not work if set to feet
    # or maybe other localizations such as screen resolution 
    if alt > 4000000:
        res=0
        rings=2
    elif alt >1600000:
        res=1
        rings=2
    elif alt >540000:
        res=2
        rings=3
    elif alt >175000:
        res=3
        rings=3
    elif alt >65000:
        res=4
        rings=4
    elif alt >30000:
        res=5
        rings=5
    elif alt >10000:
        res=6
        rings=6
    elif alt >3800:
        res=7
        rings=7
    elif alt >1300:
        res=8
        rings=8
    elif alt >550:
        res=9
        rings=9
    elif alt >250:
        res=10
        rings=10
    elif alt >150:
        res=11
        rings=11
    elif alt >50:
        res=12
        rings=12
    else:
        res=0
        rings=12
    kml=simplekml.Kml()
    mpoly = kml.newmultigeometry()

    # generate the larger hex rings centered around the cameras center of view
    home_hex=h3.geo_to_h3(lng,lat,res)#12)
    ring=h3.k_ring(home_hex,rings)
    for h in ring:
        gjhex=h3.h3_to_geo_boundary(h,geo_json=True)
        pol=mpoly.newpolygon(extrude=True,
                                outerboundaryis=gjhex)
        pol.style.linestyle.width = 2
        pol.style.polystyle.color = simplekml.Color.changealphaint(5, simplekml.Color.white)    

    # generate the smaller hex rings centered around the cameras center of view
    home_hex_small=h3.geo_to_h3(lng,lat,res+1)#12)
    ring_small=h3.k_ring(home_hex_small,3)
    for h in ring_small:
        gjhex=h3.h3_to_geo_boundary(h,geo_json=True)
        pol=mpoly.newpolygon(extrude=True,
                                outerboundaryis=gjhex)
        pol.style.linestyle.width = 2
        pol.style.polystyle.color = simplekml.Color.changealphaint(5, simplekml.Color.red)
    


    # create the screen overlay to display the current h2 resolution
    osd=kml.newscreenoverlay()
    osd.name='Resolution'
    osd.overlayxy = simplekml.OverlayXY(x=0,y=1,xunits=simplekml.Units.fraction,
                                       yunits=simplekml.Units.fraction)
    osd.screenxy = simplekml.ScreenXY(x=15,y=15,xunits=simplekml.Units.pixels,
                                     yunits=simplekml.Units.insetpixels)
    # cannot figure out how to just put text so this is silly but generate image from text
    osd.icon.href='http://chart.apis.google.com/chart?chst=d_text_outline&chld=FFBBBB|16|h|BB0000|b|'+'R'+str(res)+' '+'R'+str(res+1)
        
    return kml.kml()

class S(BaseHTTPRequestHandler):
    def _set_response(self):
        print('set response')
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()

        # didn't try to figure out why these character are here before alt
        bbox,alt=self.path.split('CAMERA=%5C%0A%20%20%20%20%20%20')
        west,south,east,north=bbox.split(',')
        north=north.strip(';')
        garbage,west=west.split('=')

        # find the center of the map and the altitude
        bbox = bbox.split(',')
        west = float(west)
        south = float(south)
        east = float(east)
        north = float(north)
        lng = ((east - west) / 2) + west
        lat = ((north - south) / 2) + south
        polykml=geth3polys(lng,lat,float(alt))

        # send the new kml back to google earth
        self.wfile.write(polykml.encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself

        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data.decode('utf-8'))

        #self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=S, port=8000):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()

import sys
import json
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, QLabel, QSizePolicy
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWebChannel import QWebChannel
from geopy.geocoders import Nominatim

html = '''
<!DOCTYPE html>
<html>
<head>

    <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
        <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
        <script>
            L_NO_TOUCH = false;
            L_DISABLE_3D = false;
        </script>

    <style>html, body {width: 100%;height: 100%;margin: 0;padding: 0;}</style>
    <style>#map {position:absolute;top:0;bottom:0;right:0;left:0;}</style>
    <script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.js"></script>
    <script src="https://code.jquery.com/jquery-1.12.4.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.css"/>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/css/bootstrap.min.css"/>
    <link rel="stylesheet" href="https://netdna.bootstrapcdn.com/bootstrap/3.0.0/css/bootstrap.min.css"/>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.2.0/css/all.min.css"/>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.css"/>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/python-visualization/folium/folium/templates/leaflet.awesome.rotate.min.css"/>

            <meta name="viewport" content="width=device-width,
                initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
            <style>
                #map_10752484e8889439d742b34af4230171 {
                    position: relative;
                    width: 100.0%;
                    height: 100.0%;
                    left: 0.0%;
                    top: 0.0%;
                }
                .leaflet-container { font-size: 1rem; }
            </style>

</head>
<body>


            <div class="folium-map" id="map_10752484e8889439d742b34af4230171" ></div>

</body>
<script>
        var backend;
        new QWebChannel(qt.webChannelTransport, function (channel) {
            backend = channel.objects.backend;
        });

        var map_10752484e8889439d742b34af4230171 = L.map(
            "map_10752484e8889439d742b34af4230171",
            {
                center: [<latitude>, <longitude>],
                crs: L.CRS.EPSG3857,
                zoom: <zoom>,
                zoomControl: true,
                preferCanvas: false,
            }
        );

        var tile_layer_c6e2500ab5a73f09082935d0d8cbb24f = L.tileLayer(
            "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            {"attribution": "Data by \\u0026copy; \\u003ca target=\\"_blank\\" href=\\"http://openstreetmap.org\\"\\u003eOpenStreetMap\\u003c/a\\u003e, under \\u003ca target=\\"_blank\\" href=\\"http://www.openstreetmap.org/copyright\\"\\u003eODbL\\u003c/a\\u003e.", "detectRetina": false, "maxNativeZoom": 18, "maxZoom": 18, "minZoom": 0, "noWrap": false, "opacity": 1, "subdomains": "abc", "tms": false}
        ).addTo(map_10752484e8889439d742b34af4230171);

        var previous_marker = null;
        map_10752484e8889439d742b34af4230171.on('click',onClick);

        var marker_latlng = <marker_latlng>;                // Here python will inject position of initial marker, if any, like "L.latLng(55.7565, 9.4196)". If none, it will inject "null"
//      var marker_latlng = null;                           // After injection, the line will look like this line...                 
//      var marker_latlng = L.latLng(55.7565, 9.4196);      // ....or like this line                
        if (marker_latlng) {
            setMarker(marker_latlng);
            is_init_marker = false;
        };    

        function removeMarker(marker){
            previous_marker = null;
            map_10752484e8889439d742b34af4230171.removeLayer(marker);
        };

        function onDblclickMarker(e){
            removeMarker(e.target);
            sendMarkerLocationToBackend(null);
        };

	    function onMoveMarker(e){		
            sendMarkerLocationToBackend(e.target.getLatLng()); 
	    };

        function sendMarkerLocationToBackend(latlng){
            if (latlng) {
                var latitude = latlng.lat.toFixed(4),
                    longitude = latlng.lng.toFixed(4);
                var location_json = JSON.stringify({ latitude, longitude });
            };
            if (latlng == null) {
                    latitude = "",
                    longitude = "";
                    location_json = JSON.stringify({ latitude, longitude });
            };
            backend.jsonSetMarkerLocation(location_json);
        };                     

        function setMarker(latlng){
            if (previous_marker) {
                map_10752484e8889439d742b34af4230171.removeLayer(previous_marker);
            };
            var new_mark = L.marker().setLatLng(latlng).addTo(map_10752484e8889439d742b34af4230171);
            new_mark.dragging.enable();
            new_mark.on('dblclick', onDblclickMarker);
            new_mark.on('dragend', onMoveMarker);
            var latitude = latlng.lat.toFixed(4),
                longitude = latlng.lng.toFixed(4);
            new_mark.bindPopup("Latitude: " + latitude + "<br>Longitude: " + longitude );
            previous_marker = new_mark;
        };

        function onClick(e){
            setMarker(e.latlng);
            sendMarkerLocationToBackend(e.latlng);
        };
</script>
</html>
'''


class MapLocationSelector(QWidget):
    location_changed = pyqtSignal(list)

    def __init__(self, location=[55.7565, 9.4196], zoom=17, marker_location=None):
        super().__init__()
        self.setWindowTitle('Search and click Location')
        self.setGeometry(100, 100, 800, 600)

        # Create a layout for the widget
        layout = QVBoxLayout(self)

        # Create a web view to display the map
        self.map_view = MapView(location, zoom, marker_location)

        # Create a search box widget
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText('Search for a location')
        self.search_box.returnPressed.connect(self.search_location)

        # Create a label widget to display the message if location not found
        self.message_label = QLabel()

        # Create OK and Cancel buttons
        self.ok_button = QPushButton('OK')
        self.cancel_button = QPushButton('Cancel')

        # Connect button clicks to methods
        self.ok_button.clicked.connect(self.onOk)
        self.cancel_button.clicked.connect(self.onCancel)

        # Create OK and Cancel buttons
        button_widget = QWidget()  # Container widget for buttons
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 0, 0, 0)

        # Add buttons to the button layout
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        # Add the map view and widgets to the layout
        layout.addWidget(self.search_box)
        layout.addWidget(self.map_view)
        layout.addWidget(button_widget)
        layout.addWidget(self.message_label)

    def search_location(self):
        geolocator = Nominatim(user_agent='MemoryMate')
        geolocation = geolocator.geocode(self.search_box.text())
        if geolocation:
            self.message_label.setText('')
            self.map_view.html = html
            self.map_view.setLocationZoom([geolocation.latitude, geolocation.longitude])
            self.map_view.setMarkerLocation(self.map_view.marker_location)
            self.map_view.setHtml(self.map_view.html)
        else:
            self.message_label.setText('Location not found')

    def onOk(self):
        print(self.map_view.marker_location)
        if self.map_view.marker_location:
            self.location_changed.emit(self.map_view.marker_location)
        else:
            self.location_changed.emit([])
        self.close()

    def onCancel(self):
        self.close()


class MapView(QWebEngineView):
    def __init__(self, location=[55.7565, 9.4196], zoom=17, marker_location=None):
        super().__init__()

        # setup channel
        self.channel = QWebChannel()
        self.channel.registerObject('backend', self)
        self.page().setWebChannel(self.channel)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.marker_location = marker_location
        self.html = html
        self.setLocationZoom(location, zoom)
        self.setMarkerLocation(self.marker_location)
        self.setHtml(self.html)

    @pyqtSlot(str)
    def jsonSetMarkerLocation(self, result):
        location_dictionary = json.loads(result)
        if location_dictionary.get('longitude') and location_dictionary.get('latitude'):
            longitude = float(location_dictionary.get('longitude'))
            latitude = float(location_dictionary.get('latitude'))
            self.marker_location = [latitude, longitude]
        else:
            self.marker_location = None

    def setMarkerLocation(self, marker_location):
        if marker_location:
            replacement_string = "L.latLng(<latitude>, <longitude>)"
            replacement_string = replacement_string.replace("<latitude>", str(marker_location[0]), 1)
            replacement_string = replacement_string.replace("<longitude>", str(marker_location[1]), 1)
        else:
            replacement_string = "null"
        self.html = self.html.replace("<marker_latlng>", replacement_string, 1)

    def setLocationZoom(self, location, zoom=13):
        self.html = self.html.replace('<latitude>', str(location[0]), 1)
        self.html = self.html.replace("<longitude>", str(location[1]), 1)
        self.html = self.html.replace('<zoom>', str(zoom), 1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MapLocationSelector()
    widget.show()
    sys.exit(app.exec_())
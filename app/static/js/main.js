(function() {

    // The Stop model is used to structure data about stops that are returned
    // from various stop APIs.
    var Stop = Backbone.Model.extend({
        defaults: function() {
            return {
                id: -1,
                lat: 0.0,
                lon: 0.0,
                tag: "",
                title: "",
                stop_id: -1};
        }
    });

    var Stops = Backbone.Collection.extend({
        model: Stop,
        parse: function(response) {
            // The API call returns an object with a single key, 'stops', that
            // maps to the array of stop objects for the collection.
            return response.stops;
        }
    });

    // The Departure model is used to structure data about the departures that
    // are returned from various departure APIs.
    var Departure = Backbone.Model.extend({
        defaults: function() {
            return {
                stop_id: -1,
                name: "",
                route_direction: "",
                route: "",
                departure_times: []
            };
        }
    });

    var Departures = Backbone.Collection.extend({
        model: Departure,
        parse: function(response) {
            // The API call returns an object with a single key, 'departures',
            // that maps to the array of stop objects for the collection.
            return response.departures;
        }
    });

    // The StopView manages the display of stop-related data, including data
    // from the Stop model, data of the Departures for the stop (when
    // available), and a map displaying where the stop is located.
    var StopView = Backbone.View.extend({
        options: {
            template: '#stop_template',
            tagName: 'tr'
        },
        events: {
            "click .map_link": "handleShowMap",
            "click .close_map_link": "handleCloseMap",
            "click .location_map": "hideClickOnMap",
            "click": "handleClick"
        },
        initialize: function() {
            this.showingDepartures = false;
            this.template = _.template($(this.options.template).html());
            this.render();
        },
        handleShowMap: function(e) {
            // Prevent a click on the map link from toggling the 'show
            // departures' state.
            e.stopImmediatePropagation();

            var locationMap = this.$('.location_map');
            locationMap.removeClass('disabled');
            this.$('.map_link').addClass('disabled');
            this.$('.close_map_link').removeClass('disabled');

            // Create a google map widget centered at the stop location and
            // with the stop location marked with a pin.
            var latlng = new google.maps.LatLng(this.model.get('lat'),
                                                this.model.get('lon'));
            var options = {
                zoom: 18,
                center: latlng,
                mapTypeControl: false,
                navigationControlOptions: {
                    style: google.maps.NavigationControlStyle.SMALL
                },
                mapTypeId: google.maps.MapTypeId.ROADMAP
            };
            var map = new google.maps.Map(
                this.$('.location_map').get(0), options);

            var marker = new google.maps.Marker({
                position: latlng, 
                map: map
            });
        },
        handleCloseMap: function(e) {
            e.stopImmediatePropagation();

            var locationMap = this.$('.location_map');
            locationMap.addClass('disabled');
            this.$('.map_link').removeClass('disabled');
            this.$('.close_map_link').addClass('disabled');
            locationMap.children().remove();
        },
        hideClickOnMap: function(e) {
            // All this does is prevent mouse interactions in the map widget
            // from toggling the 'show departures' state.
            e.stopImmediatePropagation();
        },
        handleClick: function(e) {
            // A click on the stop toggles between showing and not showing
            // the list of upcoming departures.
            if (!this.showingDepartures) {
                var departuresUrl = '/stops/' + this.model.get('stop_id') +
                                    '/departures';
                this.departures = new Departures(null, {url: departuresUrl});
                this.departuresView = new DeparturesView({
                    collection: this.departures
                });
                this.$('.departures').append(this.departuresView.$el);

                this.showingDepartures = true;
                this.departures.fetch();
            } else {
                this.$('.departures').children().remove();
                delete this.departuresView;
                // Rather than keep around the data we'll destroy it so that
                // the page doesn't keep stale data.
                delete this.departures;
                this.showingDepartures = false;
            }
        },
        render: function() {
            var templateData = this.model.toJSON();
            // Manually calculate the distance from the user to the stop
            // and add that value to the template context.
            var latDiff = this.options.userLatitude - this.model.get('lat');
            var lonDiff = this.options.userLongitude - this.model.get('lon');
            var distance = 69.0 * Math.sqrt(Math.pow(latDiff, 2.0) +
                                            Math.pow(lonDiff, 2.0));
            _.extend(templateData, {'user_distance': distance.toFixed(2)});
            this.$el.html(this.template(templateData));
        }
    });

    // The StopsView is simply a container for the StopView views for all stops
    // near the user.
    var StopsView = Backbone.View.extend({
        options: {
            template: '#stops_template'
        },
        initialize: function() {
            this.template = _.template($(this.options.template).html());
            this.collection.on('change', this.render, this);
            this.collection.on('reset', this.render, this);
            this.collection.on('sync', this.render, this);
            this.showNoStopResults = this.options.showNoStopResultsImmediately
                                  || false;
            this.render();
            this.showNoStopResults = true;
        },
        render: function() {
            this.$el.children().remove();
            this.$el.html(this.template());

            if (0 < this.collection.size()) {
                this.$('.no_stops').addClass('disabled');
                this.$('.stops_list').removeClass('disabled');

                this.collection.each(function(model) {
                    this.$('.stops_list').append(
                        new StopView({
                            model: model,
                            userLatitude: this.options.userLatitude,
                            userLongitude: this.options.userLongitude
                        }).$el);
                }, this);
            } else {
                if (this.showNoStopResults) {
                    this.$('.no_stops').removeClass('disabled');
                    this.$('.stops_list').addClass('disabled');
                } else {
                    this.$('.no_stops').addClass('disabled');
                    this.$('.stops_list').removeClass('disabled');
                }
            }
        }
    });

    // The DepartureView view displays data about upcoming departures for a
    // single route at a single stop.
    var DepartureView = Backbone.View.extend({
        options: {
            template: '#departure_template',
            tagName: 'li'
        },
        initialize: function() {
            this.template = _.template($(this.options.template).html());
            this.render();
        },
        render: function() {
            this.$el.html(this.template(this.model.toJSON()));

            _.each(this.model.get('departure_times'), function(time) {
                // The input 'time' is just a relative number of minutes from
                // the current time. It would be more useful to give the user
                // an absolute time that the bus is supposed to arrive at.
                // I manually created the time string because I didn't want
                // the time string to includes seconds (too specific,
                // especially since the api itself isn't more specific than
                // minutes).
                var departureTime = new Date();
                departureTime.setTime(departureTime.getTime() + time * 60000);
                var hours = (departureTime.getHours() % 12) + 1;
                var minutes = ('00' + departureTime.getMinutes()).slice(-2);
                var timeString = hours + ":" + minutes +
                    (departureTime.getHours() > 11 ? ' PM' : ' AM');
                this.$('.departure_time_list').append(
                    $('<li>' + timeString +
                      ' (in ' + time + (1 === time ? ' minute' : ' minutes') +
                      ')</li>'));
            }, this);
            return this;
        }
    });

    // The DeparturesView manages the DepartureView views for all departures
    // in the collection. Typically a DeparturesView is used to represent
    // departures for all routes at a common stop, but the commonality of the
    // stop is not a requirement.
    var DeparturesView = Backbone.View.extend({
        options: {
            template: '#departures_template'
        },
        initialize: function() {
            this.template = _.template($(this.options.template).html());
            this.collection.on('change', this.render, this);
            this.collection.on('reset', this.render, this);
            this.collection.on('sync', this.render, this);

            // By default we don't want to show the 'no departures' message
            // during the initial rendering as this view is usually created
            // with an empty collection that is filled with data asyncronously.
            // Once a request for data has completed we want to explicitly
            // tell the user that there are no departures.
            // The user of this class can override this behavior by setting
            // 'showNoDeparturesImmediately' to true.
            this.showNoDepartures = this.options.showNoDeparturesImmediately
                                 || false;
            this.render();
            this.showNoDepartures = true;
        },
        render: function() {
            this.$el.children().remove();
            this.$el.html(this.template({}));

            if (0 < this.collection.size()) {
                this.$('.no_departures').addClass('disabled');
                this.collection.each(function(departure) {
                    var departureView = new DepartureView({model: departure});
                    this.$('.departures_list').append(departureView.$el);
                }, this);
            } else {
                if (this.showNoDepartures) {
                    this.$('.no_departures').removeClass('disabled');
                } else {
                    this.$('.no_departures').addClass('disabled');
                }
            }
        }
    });

    // The InputView view handles getting location information from the user.
    // Input can come either from the browser's geolocation feature (if
    // available) or from the user entering a string that will be processed
    // into location coordinates by an API.
    var InputView = Backbone.View.extend({
        options: {
            template: "#location_input_template"
        },
        events: {
            "click .geolocate_button": "geolocateUser",
            "click .search_button": "manualLocateUser",
            "keypress": "handleKeyInput"
        },
        initialize: function() {
            _.bindAll(this, 'render', 'geolocateUser');
            this.canUseGeolocation = Modernizr.geolocation;
            this.template = _.template($(this.options.template).html());
            this.render();
        },
        render: function() {
            this.$el.html(this.template());

            // If geolocation isn't available, hide the option. The user
            // can manually search for a location.
            if (!this.canUseGeolocation) {
                this.$('.geolocate_input').hide();
            }
        },
        geolocateUser: function(e) {
            // Clear any old search error messages.
            this.$('.error_message').html("");
            this.$('.search_summary').html("");

            var thisView = this;
            navigator.geolocation.getCurrentPosition(function(position) {
                thisView.userLatitude = position.coords.latitude;
                thisView.userLongitude = position.coords.longitude;
                thisView.trigger('receivedGeolocation',
                                 thisView.userLatitude,
                                 thisView.userLongitude);
            }, function() {
                thisView.canUseGeolocation = false;
            });
        },
        manualLocateUser: function(e) {
            // Clear any old search error messages.
            this.$('.error_message').html("");
            this.$('.search_summary').html("");

            search_string = this.$('.search_text_input').val();
            if (search_string) {
                // Create the url for the locate api.
                // Make sure the user's input is encoded properly.
                queryUrl = '/locate/?query=' + 
                           encodeURIComponent(search_string);

                var thisView = this;
                $.ajax({
                    url: queryUrl,
                    dataType: 'json'
                }).done(function(data, textStatus, jqXHR) {
                    if (data.lat && data.lon) {
                        if (data.place) {
                            thisView.$('.search_summary').html(
                                "Search found: " + data.place);
                        }
                        thisView.userLatitude = data.lat;
                        thisView.userLongitude = data.lon;
                        thisView.trigger('receivedGeolocation',
                                         thisView.userLatitude,
                                         thisView.userLongitude);

                    } else if (data.error) {
                        if ('multiple results' === data.error) {
                            thisView.$('.error_message').html(
                                "Your search returned multiple results. " +
                                "Please enter a more specific location.");
                        } else if ('no results' === data.error) {
                            thisView.$('.error_message').html(
                                "Your search returned no results.");
                        } else {
                            thisView.$('.error_message').html(
                                "The search engine experience an error. " +
                                "Please try your search again.");
                        }
                    }
                }).fail(function(jqXHR, textStatus, errorThrown) {
                    thisView.$('.error_message').html(
                        "The search engine experience an error. " +
                        "Please try your search again.");
                });
            }
        },
        handleKeyInput: function(e) {
            if (13 === e.which) {
                this.manualLocateUser(e);
            }
        }
    });

    // The AppView is the top-most view of the view hierarchy. It's primary
    // responsibility is to create the appropriate stops/departures views in
    // response to receiving location input from the InputView.
    var AppView = Backbone.View.extend({
        options: {
            template: "#app_template"
        },
        initialize: function() {
            this.template = _.template($(this.options.template).html());

            this.inputView = new InputView({});

            // Geolocation could come from the browser or from the
            // location api call.
            this.listenTo(this.inputView, 'receivedGeolocation',
                this.geolocationFromInput);
            this.render();
        },
        render: function() {
            this.$el.html(this.template());
            this.$('.input_view').append(this.inputView.$el);
        },
        geolocationFromInput: function(latitude, longitude) {
            var stopsUrl = '/stops/' + latitude + ',' + longitude;
            this.stops = new Stops(null, { url: stopsUrl });
            this.stopsView = new StopsView({
                collection: this.stops,
                userLatitude: latitude,
                userLongitude: longitude
            });
            this.$('.stops_view').children().remove();
            this.$('.stops_view').append(this.stopsView.$el);
            this.stops.fetch();
        }
    });

    $(function() {
        var appView = new AppView({
            el: '.app'
        });
    });
}());

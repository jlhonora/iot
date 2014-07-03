d3.json("http://localhost:7654/api/v1/iot/sensors/2/measurements?interval=day")
.header("X-SESSION-KEY", "qxoo81OOm9P4OmtjcDHw6l7M2czcdLAz0T5YukB3/DiMRFPAXiiAfJDodsSe1xNM")
.get(function(error, data) {
	data = data.response.measurements;
	var json_data = {};
	var minValue = 200000;
	var maxValue = 0;
	data.forEach(function(d) {
	  var value = parseInt(d.value);
	  if (value < minValue)
		minValue = value;
	  if (value > maxValue)
		maxValue = value;
	  json_data[Date.parse(d.created_at) / 1000] = value;
	});

	var nIntervals = 5;
	legendArray = [];
	interval = (maxValue - minValue) / nIntervals;
	for (var i = 0; i < nIntervals - 1; i++) {
	  legendArray.push(Math.round(minValue + i * interval))
	}

	var cal = new CalHeatMap();
	cal.init({
	  data: json_data,
	  range: 2,
	  legend: legendArray,
	  domain: "month",
	  start: Date.parse(data[0].created_at),
	  end: Date.parse(data[data.length - 1].created_at),
	  tooltip: true,
	  itemName: ["lap", "laps"]
	});
});


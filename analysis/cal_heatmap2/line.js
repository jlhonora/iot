//# dc.js Getting Started and How-To Guide

/* jshint globalstrict: true */
/* global dc,d3,crossfilter,colorbrewer */

// ### Create Chart Objects
// Create chart objects assocated with the container elements identified by the css selector.
// Note: It is often a good idea to have these objects accessible at the global scope so that they can be modified or filtered by other page controls.

d3.json("http://localhost:7654/api/v1/iot/sensors/2/measurements?interval=minute&date=2014-06-24")
.header("X-SESSION-KEY", "qxoo81OOm9P4OmtjcDHw6l7M2czcdLAz0T5YukB3/DiMRFPAXiiAfJDodsSe1xNM")
.get(function(error, data) {
	data = data.response.measurements;
	data[0].value = 0;
  // format our data
  var dtgFormat = d3.time.format("%Y-%m-%dT%H:%M:%S");
  
  data.forEach(function(d) { 
    d.dtg   = dtgFormat.parse(d.created_at.substr(0,19)); 
    d.mag   = d3.round(+d.value,1);
    d.depth = d3.round(+d.value,0);
  });

/******************************************************
* Step1: Create the dc.js chart objects & ling to div *
******************************************************/

  var timeChart = dc.lineChart("#activity-chart");
  var magnitudeChart = dc.barChart("#hourly-chart");
  var depthChart = dc.barChart("#histogram-chart");

/****************************************
*	Run the data through crossfilter    *
****************************************/

  var facts = crossfilter(data);  // Gets our 'facts' into crossfilter

/******************************************************
* Create the Dimensions                               *
* A dimension is something to group or filter by.     *
* Crossfilter can filter by exact value, or by range. *
******************************************************/

  // for Magnitude
  var magValue = facts.dimension(function (d) {
    return d.mag;       // group or filter by magnitude
  });
  var magValueGroupSum = magValue.group()
    .reduceSum(function(d) { return d.mag; });	// sums the magnitudes per magnitude
  var magValueGroupCount = magValue.group()
    .reduceCount(function(d) { return d.mag; }) // counts the number of the facts by magnitude

  // For datatable
  var timeDimension = facts.dimension(function (d) {
    return d.dtg;
  }); // group or filter by time

  // for Depth
  var depthValue = facts.dimension(function (d) {
    return d.depth;
  });
  var depthValueGroup = depthValue.group();
  
  // define a daily volume Dimension
  var volumeByDay = facts.dimension(function(d) {
    return d3.time.minute(d.dtg);
  });
  // map/reduce to group sum
  var volumeByDayGroup = volumeByDay.group()
    .reduceSum(function(d) { return d.value; });

/***************************************
*	Step4: Create the Visualisations   *
***************************************/
  
  // Magnitide Bar Graph Summed
  magnitudeChart.width(480)
    .height(150)
    .margins({top: 10, right: 10, bottom: 20, left: 40})
    .dimension(magValue)								// the values across the x axis
    .group(magValueGroupSum)							// the values on the y axis
	.transitionDuration(500)
    .centerBar(true)	
	.gap(1)                                            // bar width Keep increasing to get right then back off.
    .x(d3.scale.linear().domain([-0.5, 13.5]))
	.elasticY(true)
	.xAxis().tickFormat(function(v) {return v;});	

  // Depth bar graph
  depthChart.width(480)
    .height(150)
    .margins({top: 10, right: 10, bottom: 20, left: 40})
    .dimension(depthValue)
    .group(depthValueGroup)
	.transitionDuration(500)
    .centerBar(true)	
	.gap(1)                    // bar width Keep increasing to get right then back off.
    .x(d3.scale.linear().domain([0, 100]))
	.elasticY(true)
	.xAxis().tickFormat(function(v) {return v;});

  // time graph
  timeChart.width(960)
    .height(150)
    .margins({top: 10, right: 10, bottom: 20, left: 40})
    .dimension(volumeByDay)
    .group(volumeByDayGroup)
    .transitionDuration(500)
	.elasticY(true)
    .x(d3.time.scale().domain([data[0].dtg, data[data.length - 1].dtg])) // scale and domain of the graph
    .xAxis();

/****************************
* Step6: Render the Charts  *
****************************/
			
  dc.renderAll();
  
});

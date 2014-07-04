//# dc.js Getting Started and How-To Guide

/* jshint globalstrict: true */
/* global dc,d3,crossfilter,colorbrewer */

// ### Create Chart Objects
// Create chart objects assocated with the container elements identified by the css selector.
// Note: It is often a good idea to have these objects accessible at the global scope so that they can be modified or filtered by other page controls.

/******************************************************
* Step1: Create the dc.js chart objects & ling to div *
******************************************************/

var timeChart = dc.lineChart("#activity-chart");
var speedChart = dc.barChart("#speed-chart");
var activeChart = dc.pieChart("#active-chart");

var resetAll = function() {
  timeChart.filterAll();  
  speedChart.filterAll(); 
  activeChart.filterAll(); 

  dc.redrawAll();
};

d3.json("http://localhost:7654/api/v1/iot/sensors/2/measurements?interval=minute&date=2014-06-24")
.header("X-SESSION-KEY", "qxoo81OOm9P4OmtjcDHw6l7M2czcdLAz0T5YukB3/DiMRFPAXiiAfJDodsSe1xNM")
.get(function(error, data) {
  data = data.response.measurements;
  data[0].value = 0;
  // format our data
  var dtgFormat = d3.time.format("%Y-%m-%dT%H:%M:%S");

  var firstDate = null; 
  var lastDate = null; 
  var threshold = 2;
  
  data.forEach(function(d) { 
    d.dtg   = dtgFormat.parse(d.created_at.substr(0,19)); 
    d.laps = d3.round(+d.value,0);
    if (firstDate == null && d.value > threshold) {
      firstDate = d.dtg;
    }
    if (d.value > threshold) {
      lastDate = d.dtg;
    }
  });


/****************************************
* Run the data through crossfilter    *
****************************************/

  var facts = crossfilter(data);  // Gets our 'facts' into crossfilter
  var all = facts.groupAll();

/******************************************************
* Create the Dimensions                               *
* A dimension is something to group or filter by.     *
* Crossfilter can filter by exact value, or by range. *
******************************************************/

  // for laps
  var lapsDimension = facts.dimension(function (d) {
    return d.laps;       // group or filter by laps
  });
  var lapsGroupSum = lapsDimension.group()
    .reduceSum(function(d) { return d.laps; }); // sums the laps per group of laps
  var lapsGroupCount = lapsDimension.group()
    .reduceCount(function(d) { return d.laps; }); // counts the number of ocurrences of each lap count

  // For datatable
  var timeDimension = facts.dimension(function (d) {
    return d.dtg;
  }); // group or filter by time

  var lapsGroupByTime = timeDimension.group()
    .reduceSum(function(d) { return d.laps; });

  // Minutely dimension
  var minuteDimension = facts.dimension(function(d) {
    return d3.time.minute(d.dtg);
  });

  // map/reduce to group sum
  var minuteGroupSum = minuteDimension.group()
    .reduceSum(function(d) { return d.laps; });

  var activeOrNot = facts.dimension(function(d) {
    return d.laps > threshold ? "Active" : "Rest"
  });

  var activeOrNotGroup = activeOrNot.group();

  

/***************************************
* Step4: Create the Visualisations   *
***************************************/
  
  // Magnitude Bar Graph Summed
  speedChart.width(480)
    .height(200)
    .margins({top: 10, right: 10, bottom: 20, left: 40})
    .dimension(lapsDimension)                // the values across the x axis
    .group(lapsGroupCount)              // the values on the y axis
  .transitionDuration(500)
    .centerBar(true)  
  .gap(1)                                            // bar width Keep increasing to get right then back off.
    .x(d3.scale.linear().domain([0.5, 80.5]))
  .elasticY(true)
  .xAxis().tickFormat(function(v) {return v;}); 

  // time graph
  timeChart.width(940)
  .renderArea(true)
    .height(200)
    .margins({top: 10, right: 10, bottom: 20, left: 40})
    .dimension(timeDimension)
    .group(lapsGroupByTime)
    .transitionDuration(500)
  .elasticY(true)
    .x(d3.time.scale().domain([firstDate, lastDate])) // scale and domain of the graph
    .xAxis();

  activeChart
    .height(180)
    .dimension(activeOrNot)
    .group(activeOrNotGroup);
/*
    .label(function (d) {
      if (activeChart.hasFilter() && !activeChart.hasFilter(d.key))
        return "" + d.key + "(0%)";
      return "" + d.key + "(" + Math.floor(d.value / all.value() * 100) + "%)";
    });
*/

/****************************
* Step6: Render the Charts  *
****************************/
      
  dc.renderAll();
  
});

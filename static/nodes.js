async function drawNodes(nodes) {

 

    console.log(nodes)
    
    d3.select("#paper")
        .append("svg")
        .attr("id", "canvas");
        // .attr("width", '100%')
        // .attr("height", 500)
        // .style("background-color", "#FFE5B4");

d3.select("svg")
  .append("circle")
  .attr("cx", 10)           // x-coordinate of the centre
  .attr("cy", 10)           // y-coordinate of the centre
  .attr("r", 8)             // radius
  .attr("fill", "lightblue")      // makes the circle hollow
  .attr("stroke", "black")   // sets the border colour
  .attr("stroke-width", 4);  // sets the thickness of the border

d3.select("svg")
  .append("text")
  .attr("x", 10+10+5)            // horizontal position
  .attr('y', 10)            // vertical position
  .text(nodes.label)         // the actual text content
  .attr("font-family", "geist_regular")
  .attr("dominant-baseline", "central")
  .attr("font-size", "16px")
  .attr("fill", "black");    // text colour
  




// d3.select("body")
//   .append("div")
//   .html('This is a block of text with a <a href="google.com">hello</a>');

}

drawNodes(nodes_data);
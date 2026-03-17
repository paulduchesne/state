async function drawNodes(nodes) {

  section = d3.select("#screen")
    .selectAll('g')
    .data(nodes)
    .enter()
    .append("svg")
    .attr('width', 600)
    .attr('height', d => {
      const rowCount = Math.ceil(d.instances.length / 24);
      const lowestY = (rowCount - 1) * 25 + 40;
      return lowestY + 45;
    })

  section.append('text')
    .text(d => d.class_label)
    .attr('x', 0).attr('y', 30)
    .attr('class', 'regular_text')

  section.selectAll("circle")
    .data(d => d.instances)
    .enter()
    .append('text')
    .text(d => d.entity_label)
    .attr('class', 'regular_text circle_labels')
    .attr('id', (d, i) => 'text_' + d.entity_link.split('/').pop())
    .attr("x",(d,i) => ((i % 24)*25)+11+15)
    .attr("y", (d, i) => (Math.floor(i / 24) * 25) + 60+5)
    .attr("opacity",0)

  section.selectAll("circle")
    .data(d => d.instances)
    .enter()
    .append("circle")
    .attr('class', 'round')
    .attr('id', (d,i) => d.entity_link.split('/').pop())
    .attr("r", 10)
    .attr("cx",(d,i) => ((i % 24)*25)+11)
    .attr("cy", (d,i) => (Math.floor(i / 24)*25)+60)
    .attr('fill', "#dddddd")
    .attr('stroke', "black")
    .attr('stroke-width', '1px')
    .attr('opacity', 0.8)
    .on('mouseover', function (k, d) {
      d3.selectAll('.round').transition().duration(200).attr('opacity', 0.1);
      d3.select(this).transition().duration(200).attr('opacity', 0.8);;
      d3.select('#'+'text_'+d.entity_link.split('/').pop()).transition().duration(200).attr('opacity', 1)
    })
    .on('mouseout', function (k, d) {
      d3.selectAll('.round').transition().duration(200).attr('opacity', 0.8);
      d3.selectAll('.circle_labels').transition().duration(200).attr('opacity', 0);
    })
    .on('click', function (k, d) {
      window.location.href = d.entity_link;
    })
}

drawNodes(nodes_data);

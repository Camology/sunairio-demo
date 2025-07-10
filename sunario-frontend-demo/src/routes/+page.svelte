<script>
  import { onMount } from "svelte";
  import * as d3 from "d3";

  let data = [];
  let svgNode;
  // Random colors for graph, probably a way to make sure there are no intersections but just wanted to try out this tool
  let colors = Array.from({ length: 28 }, () => {
    const randomValue = Math.random();
    return d3.scaleSequential(d3.interpolateRainbow)(randomValue);
  });
  //control which dataset is visible
  let visible = Array(28).fill(false);
  let isNightMode = true;
  let viewportWidth = 0;
  let viewportHeight = 0;
  let highlightedData;
  let csvFiles = [];

  function handleResize() {
    viewportWidth = document.documentElement.clientWidth;
    viewportHeight = document.documentElement.clientHeight;
  }

  function parseCSV(text) {
    return d3.csvParse(text, (d) => ({
      date: new Date(d.datetime),
      value: +d.value,
    }));
  }

  async function loadCSV(path) {
    const response = await fetch(path);
    return parseCSV(await response.text());
  }

  function toggleVisibility(index) {
    visible[index] = !visible[index];
    if (highlightedData) {
      highlightedData.remove();
      highlightedData = null;
    }
    plotData();
  }

  function toggleNightMode() {
    isNightMode = !isNightMode;
    plotData();
  }

  function resetChart() {
    visible = Array(visible.length).fill(false);
    plotData();
  }

  function plotData() {
    const width = Math.min(viewportWidth * 0.8, 1000);
    const height = Math.min(viewportHeight * 0.6, 800);
    const margin = { top: 20, right: 30, bottom: 100, left: 60 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    d3.select(svgNode).selectAll("*").remove();

    const svg = d3
      .select(svgNode)
      .attr("width", width)
      .attr("height", height)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`)
      .style("border", "none");

    svg
      .append("rect")
      .attr("width", innerWidth)
      .attr("height", innerHeight)
      .attr("fill", isNightMode ? "#121212" : "white");

    const allData = data.flat();
    const xScale = d3
      .scaleTime()
      .domain(d3.extent(allData, (d) => d.date))
      .range([0, innerWidth]);

    const yScale = d3
      .scaleLinear()
      .domain([
        d3.min(allData, (d) => d.value) - 10000,
        d3.max(allData, (d) => d.value),
      ])
      .range([innerHeight, 0]);

    const xAxis = d3.axisBottom(xScale).tickFormat(d3.timeFormat("%Y-%m-%d"));
    svg
      .append("g")
      .attr("transform", `translate(0,${innerHeight})`)
      .call(xAxis)
      .selectAll("text")
      .style("text-anchor", "end")
      .attr("dx", "-1.2em")
      .attr("dy", ".15em")
      .attr("transform", "rotate(-45)")
      .attr("fill", isNightMode ? "white" : "black");

    svg
      .append("g")
      .call(d3.axisLeft(yScale))
      .selectAll("text")
      .attr("fill", isNightMode ? "white" : "black");

    if (!highlightedData) {
      highlightedData = d3
        .select(svgNode.parentNode)
        .append("div")
        .style("opacity", 0);
    }

    data.forEach((dataset, index) => {
      if (visible[index]) {
        const line = d3
          .line()
          .x((d) => xScale(d.date))
          .y((d) => yScale(d.value));

        svg
          .append("path")
          .datum(dataset)
          .attr("fill", "none")
          .attr("stroke", colors[index])
          .attr("stroke-width", 1.5)
          .attr("d", line)
          .on("mouseover", (event, d) => {
            const bisectDate = d3.bisector((d) => d.date).left;
            const x0 = xScale.invert(d3.pointer(event, this)[0]);
            const i = bisectDate(dataset, x0, 1);
            const d0 = dataset[i - 1];
            let d1 = dataset[i] === undefined ? dataset[i - 1] : dataset[i];
            d = x0 - d0.date > d1.date - x0 ? d1 : d0;

            const [x, y] = d3.pointer(event, svgNode);

            highlightedData.transition().duration(200).style("opacity", 1);
            highlightedData
              .html(
                `Dataset: ${csvFiles[index]} <br/>Date: ${d.date.toISOString().slice(0, 19)}<br/>Value: ${d.value}`
              )
              .style("left", `${x + margin.left}px`)
              .style("top", `${y + margin.top}px`)
              .style("color", colors[index]);
          })
          .on("mouseout", () =>
            highlightedData.transition().duration(300).style("opacity", 0)
          );
      }
    });
  }

  //Should probably come up with a smarter way to do this but works for this demo
  onMount(async () => {
    csvFiles = [
      "/data/hourly_data_0.25P.csv",
      "/data/hourly_data_0.5P.csv",
      "/data/hourly_data_0.75P.csv",
      "/data/hourly_data_0.99P.csv",
      "/data/daily_max_0.25.csv",
      "/data/daily_max_0.5.csv",
      "/data/daily_max_0.75.csv",
      "/data/daily_max_0.99.csv",
      "/data/daily_mean_0.25.csv",
      "/data/daily_mean_0.5.csv",
      "/data/daily_mean_0.75.csv",
      "/data/daily_mean_0.99.csv",
      "/data/daily_min_0.25.csv",
      "/data/daily_min_0.5.csv",
      "/data/daily_min_0.75.csv",
      "/data/daily_min_0.99.csv",
      "/data/monthly_max_0.25.csv",
      "/data/monthly_max_0.5.csv",
      "/data/monthly_max_0.75.csv",
      "/data/monthly_max_0.99.csv",
      "/data/monthly_mean_0.25.csv",
      "/data/monthly_mean_0.5.csv",
      "/data/monthly_mean_0.75.csv",
      "/data/monthly_mean_0.99.csv",
      "/data/monthly_min_0.25.csv",
      "/data/monthly_min_0.5.csv",
      "/data/monthly_min_0.75.csv",
      "/data/monthly_min_0.99.csv",
    ];

    data = await Promise.all(csvFiles.map(loadCSV));
    plotData();
    window.addEventListener("resize", handleResize);
    handleResize();
  });

  function cleanup() {
    window.removeEventListener("resize", handleResize);
    if (highlightedData) highlightedData.remove();
  }

  $: if (data.length > 0) plotData();
</script>

<div
  class="chart-container"
  style="--chart-bg-color: {isNightMode ? '#121212' : 'white'};"
>
  <div style="width: 100%; height: 100%;">
    <svg bind:this={svgNode}></svg>
  </div>
  <div class="controls">
    {#each ["Hourly", "Daily Max", "Daily Mean", "Daily Min", "Monthly Max", "Monthly Mean", "Monthly Min"] as type, typeIndex}
      <div style="display: flex; justify-content: flex-start; padding: 10px;">
        {#each [25, 50, 75, 99] as percentile, percentileIndex}
          <button
            class="button"
            on:click={() => toggleVisibility(typeIndex * 4 + percentileIndex)}
          >
            {`${visible[typeIndex * 4 + percentileIndex] ? "Hide" : "Show"} ${type} ${percentile}% Data`}
          </button>
        {/each}
      </div>
    {/each}
    <button on:click={toggleNightMode}>
      {isNightMode ? "Day Mode" : "Night Mode"}
    </button>
    <button on:click={resetChart}>Reset Chart</button>
  </div>
</div>

<svelte:window on:resize={handleResize} on:beforeunload={cleanup} />

<!-- CSS is definitely not my strong suit if thats not blatantly obvious  -->

<style>
  :global body {
    margin: 0 !important;
    padding: 0;
    height: 100%;
    width: 100%;
    border: 0;
  }

  :global .chart-container {
    height: 100vh;
    width: 100vw;
    background-color: var(--chart-bg-color);
    display: flex;
    flex-direction: column;
    transition: background-color 0.3s;
    position: relative;
    border: none;
  }

  /*borrowed CSS from bootstrap */
  :global .button {
    cursor: pointer;
    outline: 0;
    color: #fff;
    background-color: #8021fd;
    border-color: #0d6efd;
    display: inline-block;
    font-weight: 400;
    line-height: 1.5;
    text-align: center;
    border: 1px solid transparent;
    padding: 6px 12px;
    font-size: 14px;
    border-radius: 0.25rem;
    transition:
      color 0.15s ease-in-out,
      background-color 0.15s ease-in-out,
      border-color 0.15s ease-in-out,
      box-shadow 0.15s ease-in-out;
    margin-left: 2px;
  }
</style>

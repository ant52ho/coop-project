// import { interpolateInferno } from "d3-scale-chromatic";
import { interpolateRainbow } from "d3-scale-chromatic";
// for colorscale, use interpolateRainbow

const colorScale = interpolateRainbow;
const colorRangeInfo = {
  colorStart: 0,
  colorEnd: 1,
  useEndAsStart: false,
};

function calculatePoint(i, intervalSize, colorRangeInfo) {
  var { colorStart, colorEnd, useEndAsStart } = colorRangeInfo;
  return useEndAsStart
    ? colorEnd - i * intervalSize
    : colorStart + i * intervalSize;
}

export function interpolateColors(dataLength, colorScale, colorRangeInfo) {
  var { colorStart, colorEnd } = colorRangeInfo;
  var colorRange = colorEnd - colorStart;
  var intervalSize = colorRange / dataLength;
  var i, colorPoint;
  var colorArray = [];

  for (i = 0; i < dataLength; i++) {
    colorPoint = calculatePoint(i, intervalSize, colorRangeInfo);
    colorArray.push(colorScale(colorPoint));
  }

  return colorArray;
}

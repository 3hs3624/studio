'use strict';
(()=>{if(!document.getElementById('process-create'))return;const graph=JSON.parse(document.getElementById('process-initial-graph').textContent);window.buildProcessGraph=()=>JSON.parse(JSON.stringify(graph));})();

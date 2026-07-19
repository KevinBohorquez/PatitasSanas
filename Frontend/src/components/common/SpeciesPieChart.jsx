import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import { useFetch } from '../../hooks/useFetch';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

const CenterTextPlugin = {
  id: 'centerText',
  afterDraw(chart) {
    const { width, height, ctx } = chart;
    ctx.save();
    const total = chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.font = '500 28px system-ui, sans-serif';
    ctx.fillStyle = '#2c2c2a';
    ctx.fillText(total, width / 2, height / 2 - 10);
    ctx.font = '400 13px system-ui, sans-serif';
    ctx.fillStyle = '#888780';
    ctx.fillText('pacientes', width / 2, height / 2 + 16);
    ctx.restore();
  }
};
ChartJS.register(CenterTextPlugin);

const SpeciesPieChart = () => {
  const { data } = useFetch('/dashboard/mascotas-por-especie', {
    transform: (d) => ({
      perros: d.find((item) => item.especie === 'Perro')?.total || 0,
      gatos: d.find((item) => item.especie === 'Gato')?.total || 0,
    }),
  });
  const speciesData = data ?? { perros: 0, gatos: 0 };

  const total = speciesData.perros + speciesData.gatos;
  const pctDogs = total > 0 ? Math.round((speciesData.perros / total) * 100) : 0;
  const pctCats = total > 0 ? Math.round((speciesData.gatos / total) * 100) : 0;

  const chartData = {
    labels: ['Perros', 'Gatos'],
    datasets: [{
      data: [speciesData.perros, speciesData.gatos],
      backgroundColor: ['#378ADD', '#D4537E'],
      borderWidth: 3,
    }]
  };

  const options = {
    cutout: '62%',
    plugins: { legend: { display: false } },
    maintainAspectRatio: false,
  };

  return (
    <div className="stat-card">
      {/* Leyenda */}
      <div style={{ display: 'flex', gap: 16, marginBottom: 8 }}>
        <span>🟦 Perros — {pctDogs}%</span>
        <span>🟥 Gatos — {pctCats}%</span>
      </div>
      {/* Gráfica */}
      <div style={{ position: 'relative', height: 280 }}>
        <Doughnut data={chartData} options={options} />
      </div>
    </div>
  );
};

export default SpeciesPieChart;

import React from 'react';
import { Bar } from 'react-chartjs-2';
import { useFetch } from '../../hooks/useFetch';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

const ServicesBarChart = () => {
  const { data: raw } = useFetch('/dashboard/servicios-mas-solicitados?limit=5', {
    transform: (d) => ({
      labels: d.map((item) => item.nombre_servicio || item.servicio || item.nombre || 'Desconocido'),
      data: d.map((item) => item.total_solicitudes || item.cantidad || item.total || item.conteo || 0),
    }),
  });
  const chartData = raw ?? { labels: [], data: [] };

  const data = {
    labels: chartData.labels,
    datasets: [
      {
        label: 'Solicitudes',
        data: chartData.data,
        backgroundColor: '#378ADD',
        borderRadius: 6,
        borderWidth: 0,
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        callbacks: {
          label: (context) => ` ${context.raw} solicitudes`
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          stepSize: 1,
          precision: 0
        },
        grid: {
          color: '#e0e0e0',
          drawBorder: false,
        }
      },
      x: {
        grid: {
          display: false
        }
      }
    }
  };

  // Verificacion de que existen registro de serivicos
  const hasNoData = chartData.data.length == 0;

  return (
    <div className="stat-card">
      <div style={{ marginBottom: '16px' }}>
        <h3 style={{ margin: 0, fontSize: '18px', color: '#2c2c2a' }}>
          Servicios mas solicitados
        </h3>
        <span style={{ fontSize: '13px', color: '#888780' }}>
          Demanda por tipo de servicio
        </span>
      </div>

      <div style={{ position: 'relative', height: 280 }}>
        {hasNoData ? (
          /*Mensaje en caso no existan datos*/
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: '100%',
            color: '#888780',
            fontSize: '16px',
            fontWeight: '500',
            textAlign: 'center'
          }}>
            No existen citas atendidas en el sistema
          </div>
        ) :
          (
            <Bar data={data} options={options} />
          )
        }
      </div>
    </div>
  );
};

export default ServicesBarChart;

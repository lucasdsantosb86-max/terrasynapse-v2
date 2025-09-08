import React, { useEffect, useState } from "react";
import { Leaf, Thermometer, Droplets, CloudRain, Wind } from "lucide-react";
import {
  ResponsiveContainer,
  LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip,
  BarChart, Bar
} from "recharts";

/* ===== Tipos ===== */
interface WeatherData {
  temperature: number;
  humidity: number;
  windSpeed: number;
  pressure: number;
  et0: number;
  rainfall: number;
  condition: string;
}

interface NdviData {
  current: number;
  status: string;
  trend: string;
  color: string;
}

type Alert = {
  id: number;
  type: "warning" | "info" | "error" | "success";
  message: string;
  priority: "low" | "medium" | "high";
  time: string;
};

/* ===== Dados fake para gráficos ===== */
type Point = { dia: string; et0: number };
type Comm = { nome: string; preco: number };

const et0Data: Point[] = [
  { dia: "Seg", et0: 4.2 }, { dia: "Ter", et0: 4.8 }, { dia: "Qua", et0: 5.1 },
  { dia: "Qui", et0: 4.6 }, { dia: "Sex", et0: 5.0 }, { dia: "Sáb", et0: 4.3 }, { dia: "Dom", et0: 4.9 },
];

const commoditiesData: Comm[] = [
  { nome: "Soja",  preco: 154 },
  { nome: "Milho", preco: 72  },
  { nome: "Café",  preco: 1060},
];

/* ===== Componentes tipados ===== */
type MetricCardProps = {
  icon: React.ComponentType<{ size?: number; className?: string }>;
  title: string;
  value: React.ReactNode;
  delta?: React.ReactNode;
  color?: "green" | "blue" | "orange" | "purple";
};

const MetricCard: React.FC<MetricCardProps> = ({ icon: Icon, title, value, delta, color = "green" }) => (
  <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300 transform hover:scale-105">
    <div className="flex items-center justify-between mb-4">
      <div className={`p-3 rounded-xl bg-gradient-to-r ${
        color === "green"  ? "from-green-100 to-green-200" :
        color === "blue"   ? "from-blue-100 to-blue-200" :
        color === "orange" ? "from-orange-100 to-orange-200" : "from-purple-100 to-purple-200"
      }`}>
        <Icon size={22} className="text-gray-700" />
      </div>
      <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-600">Atualizado</span>
    </div>
    <div className="text-sm text-gray-500">{title}</div>
    <div className="text-2xl font-bold">{value}</div>
    {delta && <div className="text-xs text-gray-500 mt-1">{delta}</div>}
  </div>
);

const AlertCard: React.FC<{ alert: Alert }> = ({ alert }) => (
  <div
    className={`p-4 rounded-xl border-l-4 ${
      alert.type === "warning" ? "bg-orange-50 border-orange-400" :
      alert.type === "error"   ? "bg-red-50 border-red-400" :
      alert.type === "success" ? "bg-green-50 border-green-400" :
                                 "bg-blue-50 border-blue-400"
    }`}
  >
    <div className="flex items-center justify-between">
      <div className="font-medium">{alert.message}</div>
      <div className="text-xs text-gray-500">{alert.time}</div>
    </div>
    <div className="text-xs text-gray-500 mt-1">Prioridade: {alert.priority}</div>
  </div>
);

/* ===== Tela principal ===== */
export default function TerraSynapseEnterprise() {
  const [weatherData, setWeatherData] = useState<WeatherData | null>(null);
  const [ndviData, setNdviData] = useState<NdviData | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);

  useEffect(() => {
    // valores iniciais
    setWeatherData({
      temperature: 24.5,
      humidity: 68,
      windSpeed: 12.3,
      pressure: 1013.2,
      et0: 4.8,
      rainfall: 0.0,
      condition: "Parcialmente nublado"
    });

    setNdviData({
      current: 0.75,
      status: "Saudável",
      trend: "+0.02",
      color: "#4CAF50"
    });

    setAlerts([
      { id: 1, type: "warning", message: "ET0 elevada detectada - considere irrigação", priority: "medium", time: "14:30" },
      { id: 2, type: "info",    message: "Condições ideais para aplicação foliar",      priority: "low",    time: "13:45" }
    ]);

    const timer = window.setInterval(() => {
      // Exemplo: oscila a ET0 levemente
      setWeatherData(prev =>
        prev ? { ...prev, et0: +(prev.et0 + (Math.random() - 0.5) * 0.4).toFixed(2) } : prev
      );
    }, 8000);

    return () => window.clearInterval(timer);
  }, []);

  return (
    <div className="min-h-screen bg-[var(--bg)] text-[var(--text)]">
      {/* Navbar */}
      <div className="w-full flex items-center gap-2 px-5 py-3 shadow-md"
           style={{ background: "var(--ts-green)", color: "#fff" }}>
        <Leaf size={22} />
        <div className="font-bold">TerraSynapse</div>
        <div className="ml-auto opacity-90">V2.0 • Frontend React</div>
      </div>

      {/* Container */}
      <div className="max-w-[1100px] mx-auto px-4 py-6">
        {/* KPIs */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-black/5">
          <div className="flex items-center gap-2 mb-3">
            <h3 className="text-lg font-semibold">Visão Geral</h3>
            <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: "var(--ts-green-2)", color: "#fff" }}>
              TerraSynapse
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            <MetricCard
              icon={Thermometer}
              title="Temperatura"
              value={`${weatherData?.temperature ?? "-"}°C`}
              delta={`${weatherData?.humidity ?? "-"}% umidade`}
              color="orange"
            />
            <MetricCard
              icon={Droplets}
              title="ET0"
              value={`${weatherData?.et0 ?? "-"} mm/dia`}
              delta={(weatherData?.et0 ?? 0) > 5 ? "Irrigação recomendada" : "Normal"}
              color="blue"
            />
            <MetricCard
              icon={Leaf}
              title="NDVI"
              value={ndviData?.current ?? "-"}
              delta={`${ndviData?.trend ?? ""} ${ndviData?.status ?? ""}`}
              color="green"
            />
            <MetricCard
              icon={Wind}
              title="Vento"
              value={`${weatherData?.windSpeed ?? "-"} km/h`}
              delta={`${weatherData?.pressure ?? "-"} hPa`}
              color="purple"
            />
          </div>
        </div>

        {/* Grids */}
        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-white rounded-2xl p-5 shadow-sm border border-black/5">
            <h3 className="text-lg font-semibold mb-2">Clima — ET₀ (7 dias)</h3>
            <div className="h-[260px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={et0Data} margin={{ left: 10, right: 10, top: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="dia" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="et0" stroke="var(--ts-green)" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-white rounded-2xl p-5 shadow-sm border border-black/5">
            <h3 className="text-lg font-semibold mb-2">Mercado — Commodities (R$)</h3>
            <div className="h-[260px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={commoditiesData} margin={{ left: 10, right: 10, top: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="nome" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="preco" fill="var(--ts-green-2)" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Alertas */}
        <div className="mt-4 bg-white rounded-2xl p-5 shadow-sm border border-black/5">
          <h3 className="text-lg font-semibold mb-2">Alertas</h3>
          <div className="space-y-3">
            {alerts.map((alert) => (
              <AlertCard key={alert.id} alert={alert} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

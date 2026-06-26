export default function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="stat-card" role="group" aria-label={label}>
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div>
    </div>
  );
}

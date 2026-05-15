export default function Spinner({ size = 18, color = "#839705" }) {
  return (
    <div
      className="anim-spinFast flex-shrink-0 rounded-full"
      style={{
        width: size, height: size,
        border: `2px solid ${color}33`,
        borderTopColor: color,
      }}
    />
  );
}
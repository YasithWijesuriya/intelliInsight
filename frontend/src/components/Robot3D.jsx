import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, useGLTF } from "@react-three/drei";
import { useRef } from "react";

function Model() {
  const ref = useRef();

  const { scene } = useGLTF("/models/robot.glb");

  useFrame((state) => {
    const t = state.clock.getElapsedTime();

    // smooth floating
    ref.current.position.y = -1.2 + Math.sin(t * -1.2) * 0.03;

    // gentle left-right motion
    ref.current.rotation.y = Math.sin(t * 0.3) * 0.40;
  });

  return (
    <primitive
      ref={ref}
      object={scene}
      scale={1.55}
      position={[1, -1, 0]}
      rotation={[0, Math.PI, 0]}
    />
  );
}

export default function Robot3D() {
  return (
    <div
      style={{
        width: "100%",
        height: "650px",
        background: "transparent",
        paddingBottom:"200px",
      }}
    >
      <Canvas
        camera={{
          position: [-1.2, 0, 4],
          fov: 60,
        }}
        style={{
          background: "transparent",
        }}
      >
        {/* soft environment light */}
        <ambientLight intensity={0.9} />
        
        <directionalLight position={[5, 5, 5]} intensity={1} />
        <directionalLight position={[-5, 5, -5]} intensity={0.5} />
        
        <Model />

        <OrbitControls
          enableZoom={false}
          enablePan={false}
          // enableRotate={false}
        />
      </Canvas>
    </div>
  );
}

useGLTF.preload("/models/robot.glb");
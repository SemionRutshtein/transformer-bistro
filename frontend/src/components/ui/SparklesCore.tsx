import { useId, useState, useCallback } from "react";
import { ParticlesProvider, Particles } from "@tsparticles/react";
import { loadSlim } from "@tsparticles/slim";
import type { Engine } from "@tsparticles/engine";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

type SparklesProps = {
  id?: string;
  className?: string;
  background?: string;
  minSize?: number;
  maxSize?: number;
  speed?: number;
  particleColor?: string;
  particleDensity?: number;
};

export const SparklesCore = (props: SparklesProps) => {
  const {
    id,
    className,
    background,
    minSize,
    maxSize,
    speed,
    particleColor,
    particleDensity,
  } = props;

  const [ready, setReady] = useState(false);
  const generatedId = useId();

  const initEngine = useCallback(async (engine: Engine) => {
    await loadSlim(engine);
    setReady(true);
  }, []);

  return (
    <ParticlesProvider init={initEngine}>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: ready ? 1 : 0 }}
        transition={{ duration: 1 }}
        className={cn(className)}
        style={{ width: "100%", height: "100%" }}
      >
        {ready && (
          <Particles
            id={id ?? generatedId}
            style={{ width: "100%", height: "100%" }}
            options={{
              background: { color: { value: background ?? "transparent" } },
              fullScreen: { enable: false, zIndex: 1 },
              fpsLimit: 120,
              interactivity: {
                events: {
                  onClick: { enable: true, mode: "push" },
                  onHover: { enable: false, mode: "repulse" },
                },
                modes: {
                  push: { quantity: 4 },
                  repulse: { distance: 200, duration: 0.4 },
                },
              },
              particles: {
                color: { value: particleColor ?? "#ffffff" },
                move: {
                  direction: "none",
                  enable: true,
                  outModes: { default: "out" },
                  random: false,
                  speed: { min: 0.1, max: 1 },
                  straight: false,
                },
                number: {
                  density: { enable: true, width: 400, height: 400 },
                  value: particleDensity ?? 120,
                },
                opacity: {
                  value: { min: 0.1, max: 1 },
                  animation: {
                    enable: true,
                    speed: speed ?? 4,
                    sync: false,
                  },
                },
                shape: { type: "circle" },
                size: {
                  value: { min: minSize ?? 1, max: maxSize ?? 3 },
                },
              },
              detectRetina: true,
            }}
          />
        )}
      </motion.div>
    </ParticlesProvider>
  );
};

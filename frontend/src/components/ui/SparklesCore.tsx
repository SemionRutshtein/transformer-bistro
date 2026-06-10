import { useId, useEffect, useState, useCallback } from "react";
import { ParticlesProvider, Particles } from "@tsparticles/react";
import { loadSlim } from "@tsparticles/slim";
import type { Engine } from "@tsparticles/engine";
import { cn } from "@/lib/utils";
import { motion, useAnimation } from "framer-motion";

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

  const [loaded, setLoaded] = useState(false);
  const controls = useAnimation();
  const generatedId = useId();

  const init = useCallback(async (engine: Engine) => {
    await loadSlim(engine);
  }, []);

  useEffect(() => {
    if (loaded) {
      void controls.start({ opacity: 1, transition: { duration: 1 } });
    }
  }, [loaded, controls]);

  return (
    <ParticlesProvider init={init}>
      <motion.div animate={controls} className={cn("opacity-0", className)}>
        <Particles
          id={id ?? generatedId}
          className="h-full w-full"
          particlesLoaded={async () => setLoaded(true)}
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
      </motion.div>
    </ParticlesProvider>
  );
};

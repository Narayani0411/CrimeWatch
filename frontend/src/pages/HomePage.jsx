import React from "react";
import { Link } from "react-router-dom";
import { Shield, Video, Bell, Users } from "lucide-react";
import camera from "../assets/cctv.png";

const HomePage = () => {
  return (
    <div
      className="min-h-screen w-full fade-in transition-all duration-700 bg-[linear-gradient(135deg,_#fef6fb_0%,_#f3f6ff_45%,_#e8faff_100%)] dark:bg-[linear-gradient(135deg,_#0d0f14_0%,_#151821_45%,_#1b1f29_100%)]"
      style={{
        background:
          "linear-gradient(135deg, var(--bg-color) 0%, #f3f6ff 45%, #e8faff 100%)",
        color: "var(--text-color)",
      }}
    >
      {/* 🌅 HERO SECTION */}
      <section className="flex flex-col md:flex-row items-center justify-between px-8 md:px-16 py-20 max-w-7xl mx-auto gap-10">
        {/* TEXT CARD */}
        <div
          className="p-10 rounded-3xl border border-[var(--border-color)] bg-[var(--card-bg)] shadow-md hover:shadow-xl hover:-translate-y-2 transition-all duration-500"
        >
          <h1 className="text-5xl font-extrabold leading-snug mb-4 text-[var(--accent)]">
            CrimeWatch.
          </h1>
          <h2 className="text-4xl font-bold mb-6">Intelligent Real-Time Crime Detection.</h2>

          <p className="leading-relaxed mb-8 opacity-90">
            <strong>CrimeWatch</strong> uses <strong>AI</strong> and{" "}
            <strong>Computer Vision</strong> to transform traditional
            surveillance into proactive safety monitoring. Detect weapons,
            violence, and suspicious activity in real time with ease.
          </p>

          <div className="flex gap-4 pt-2">
            <Link to="/signin" className="btn">
              🚀 Get Started
            </Link>

            <a
              href="#about"
              className="btn"
              style={{
                background: "var(--link-color)",
                color: "#fff",
              }}
            >
              Learn More
            </a>
          </div>
        </div>

        {/* CAMERA CARD */}
        <div
          className="p-8 rounded-3xl shadow-md border border-[var(--border-color)] bg-[var(--card-bg)] hover:scale-105 transition-transform duration-500"
        >
          <img
            src={camera}
            alt="CCTV Camera"
            className="w-80 md:w-96 rounded-xl animate-float"
          />
        </div>
      </section>

      {/* 🧠 ABOUT SECTION */}
      <section
        id="about"
        className="max-w-6xl mx-auto my-20 p-10 rounded-3xl text-center border border-[var(--border-color)] bg-[var(--card-bg)] shadow-md hover:shadow-xl hover:-translate-y-2 transition-all duration-500"
      >
        <h2 className="text-3xl font-bold mb-6 text-[var(--accent)]">
          About CrimeWatch
        </h2>
        <p className="leading-relaxed opacity-90 max-w-3xl mx-auto">
          CrimeWatch revolutionizes surveillance using AI and deep learning.
          It continuously monitors live feeds to detect violence, weapons, and
          anomalies — instantly alerting authorities to reduce risks and improve
          emergency response efficiency.
        </p>
      </section>

      {/* ⚙️ FEATURES SECTION */}
      <section
        className="max-w-6xl mx-auto my-20 p-10 rounded-3xl border border-[var(--border-color)] bg-[var(--card-bg)] shadow-md hover:shadow-xl hover:-translate-y-2 transition-all duration-500"
      >
        <h2 className="text-3xl font-bold mb-10 text-center text-[var(--accent)]">
          Core Functionalities
        </h2>

        <div className="grid gap-10 md:grid-cols-3">
          {[
            {
              icon: <Video size={42} className="mx-auto mb-4 text-[var(--accent)]" />,
              title: "Real-Time Video Analysis",
              desc: "AI models instantly detect violence, weapons, and suspicious movements from live camera feeds.",
            },
            {
              icon: <Bell size={42} className="mx-auto mb-4 text-[var(--accent)]" />,
              title: "Instant Notifications",
              desc: "Automatically alerts via email or dashboard when a potential threat is detected.",
            },
            {
              icon: <Users size={42} className="mx-auto mb-4 text-[var(--accent)]" />,
              title: "Collaborative Monitoring",
              desc: "Allows multiple authorized users to monitor and respond together in real time.",
            },
          ].map((feature, index) => (
            <div
              key={index}
              className="p-8 rounded-2xl shadow-md hover:shadow-xl hover:-translate-y-2 transition-all duration-300 border border-[var(--border-color)] bg-[var(--card-bg)]"
            >
              {feature.icon}
              <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
              <p className="text-sm leading-relaxed opacity-90">{feature.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* 🛡️ MISSION SECTION */}
      <section
        className="max-w-6xl mx-auto my-20 p-10 text-center rounded-3xl border border-[var(--border-color)] bg-[var(--card-bg)] shadow-md hover:shadow-xl hover:-translate-y-2 transition-all duration-500"
      >
        <Shield size={50} className="mx-auto mb-4 text-[var(--accent)]" />
        <h2 className="text-3xl font-bold mb-4 text-[var(--accent)]">Our Mission</h2>
        <p className="leading-relaxed max-w-3xl mx-auto opacity-90">
          CrimeWatch enhances public safety by transforming passive camera
          systems into intelligent networks that prevent crimes and protect
          lives in real time.
        </p>
      </section>

      {/* 🌍 FOOTER */}
      <footer
        className="py-6 text-center border-t border-[var(--border-color)] transition-all duration-700 bg-[var(--card-bg)]"
      >
        <p className="text-sm opacity-80">
          © {new Date().getFullYear()} <strong>CrimeWatch</strong> | Empowering
          Public Safety with AI
        </p>
      </footer>
    </div>
  );
};

export default HomePage;

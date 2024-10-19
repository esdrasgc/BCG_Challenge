"use client"; // Adicione isso no topo

import LocationSelector from "../components/LocationSelector";
import Chat from "../components/ai-chat";
import { useEffect, useState } from "react";

export default function Home() {
  const [id_localstorage, setId_localstorage] = useState(null);

  useEffect(() => {
    const id = localStorage.getItem("id");
    setId_localstorage(id);
  }, []);

  return (
    <div>
      {!id_localstorage ? (
        <div>
          <LocationSelector />
        </div>
      ) : (
        <div>
          <Chat />
        </div>
      )}
    </div>
  );
}

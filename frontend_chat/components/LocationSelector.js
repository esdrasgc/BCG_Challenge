"use client";

import React, { useEffect, useState } from "react";
import { Autocomplete, TextField, Button as MuiButton, CircularProgress } from "@mui/material";
import axios from "axios";
import { Leaf } from "lucide-react";

export default function LocationSelector() {
  const [states, setStates] = useState([]);
  const [selectedState, setSelectedState] = useState(null);
  const [cities, setCities] = useState([]);
  const [selectedCity, setSelectedCity] = useState(null);
  const [loadingCities, setLoadingCities] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchStates = async () => {
      try {
        const response = await axios.get(
          "https://servicodados.ibge.gov.br/api/v1/localidades/estados?orderBy=nome"
        );
        const simplifiedStates = response.data.map((state) => ({
          id: state.id,
          abbreviation: state.sigla,
          name: state.nome,
        }));
        setStates(simplifiedStates);
      } catch (error) {
        console.error("Error fetching states:", error);
      }
    };
    fetchStates();
  }, []);

  useEffect(() => {
    if (selectedState) {
      const fetchCities = async () => {
        setLoadingCities(true);
        try {
          const response = await axios.get(
            `https://servicodados.ibge.gov.br/api/v1/localidades/estados/${selectedState.id}/municipios?orderBy=nome`
          );
          const simplifiedCities = response.data.map((city) => ({
            id: city.id,
            name: city.nome,
          }));
          setCities(simplifiedCities);
        } catch (error) {
          console.error("Error fetching cities:", error);
        } finally {
          setLoadingCities(false);
        }
      };
      fetchCities();
    } else {
      setCities([]);
      setSelectedCity(null);
    }
  }, [selectedState]);

  const handleSubmit = () => {
    if (selectedState && selectedCity) {
      setLoading(true);
      fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ state: selectedState, city: selectedCity }),
      })
      .then((response) => response.json())
      .then((response) => {
        if (response.id) {
          localStorage.setItem("id", response.id);
          setLoading(false);
          window.location.reload();
        } else {
          console.error("Error starting chat:", response.statusText);
        }
      })
      .catch((error) => {
        console.error("Error with fetch:", error);
        setLoading(false);
      });
    }
  };
  
  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-green-50 border-b border-green-200 p-4">
        <div className="container mx-auto flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <Leaf className="h-6 w-6 text-green-800" />
            <h1 className="text-xl font-semibold text-green-800">Climate AI</h1>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-md bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4 text-gray-900">Bem vindo ao assistente climático!</h2>
          <h2 className="text-l font-semibold mb-4 text-gray-600">Para iniciar, por favor, selecione a UF e Município</h2>
          <Autocomplete
            options={states}
            getOptionLabel={(option) => `${option.name} (${option.abbreviation})`}
            value={selectedState}
            onChange={(event, newValue) => setSelectedState(newValue)}
            renderInput={(params) => <TextField {...params} label="Selecione o estado" variant="outlined" />}
            className="mb-4"
          />
          <Autocomplete
            options={cities}
            getOptionLabel={(option) => option.name}
            value={selectedCity}
            onChange={(event, newValue) => setSelectedCity(newValue)}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Selecione o município"
                variant="outlined"
                InputProps={{
                  ...params.InputProps,
                  endAdornment: (
                    <>
                      {loadingCities ? <CircularProgress color="inherit" size={20} /> : null}
                      {params.InputProps.endAdornment}
                    </>
                  ),
                }}
              />
            )}
            disabled={!selectedState}
            className="mb-4"
          />
          <MuiButton
            variant="contained"
            color="primary"
            fullWidth
            onClick={handleSubmit}
            disabled={!selectedState || !selectedCity}
          >
            {loading ? (
              <CircularProgress color="inherit" size={20} />
            ) : (
              "Start Chat"
            )}
          </MuiButton>
        </div>
      </div>
    </div>
  );
}
"use client";

import React, { useEffect, useState } from "react";
import { Autocomplete, TextField, Button, CircularProgress } from "@mui/material";
import axios from "axios"; 

export default function LocationSelector() {
  const [states, setStates] = useState([]);
  const [selectedState, setSelectedState] = useState(null);
  const [cities, setCities] = useState([]);
  const [selectedCity, setSelectedCity] = useState(null);
  const [loadingCities, setLoadingCities] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Fetch states from the IBGE API and map to simplified types
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
      // Fetch cities based on the selected state and map to simplified types
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
        setLoading(false);  // Make sure to handle loading state even on error
      });
    }
  };
  
  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-50 p-4">
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
        <Button
          variant="contained"
          color="primary"
          fullWidth
          onClick={handleSubmit}
          disabled={!selectedState || !selectedCity}
        >

          {
            loading ? (
              <CircularProgress color="inherit" size={20}  />
            ) : (
              "Start Chat"
            )
          }
    
        </Button>
      </div>
    </div>
  );
}

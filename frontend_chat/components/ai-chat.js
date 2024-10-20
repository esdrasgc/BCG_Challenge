"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  MessageSquare, 
  BarChart2, 
  X, 
  BarChart, 
  FileText, 
  Type, 
  Languages
} from "lucide-react";

function Chat() {
  const [isKpiOpen, setIsKpiOpen] = useState(false);
  const [hasChatStarted, setHasChatStarted] = useState(true);
  const [digitando, setDigitando] = useState(false); // 'digitando' means 'typing' in Portuguese
  const [id, setId] = useState(localStorage.getItem("id"));
  const [cities, setCities] = useState([]);
  const [key_indicators, setKey_indicators] = useState([]);
  const [prompt, setPrompt] = useState("");
  const [messages, setMessages] = useState([]); // State to store messages

  useEffect(() => {
    // Fetch chat data when component mounts
    fetch(`http://localhost:8000/chat/${id}`)
      .then((response) => response.json())
      .then((data) => { 
        console.log(data);
        setCities(data.city);
        
        setKey_indicators(data.key_indicators);
      });
  }, [id]);

  console.log(messages);
  const toggleKpi = () => setIsKpiOpen(!isKpiOpen);

  const handleSendMessage = () => {
    if (prompt.trim() === "") return;
    const userMessage = { sender: "Você", text: prompt }; // 'Você' means 'You' in Portuguese
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setPrompt("");
    setDigitando(true);
    sendPrompt(prompt);
  };

  const sendPrompt = (prompt) => {
    fetch("http://localhost:8000/message", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        chat_id: id,
        query: prompt,
      }),
    })
      .then((response) => response.json())
      .then((data) => { 
        console.log(data);
        const aiMessage = { sender: "AI", text: data.response };
        setMessages((prevMessages) => [...prevMessages, aiMessage]);
        setDigitando(false);
      })
      .catch((error) => {
        console.error(error);
        const errorMessage = { sender: "AI", text: "Desculpe, ocorreu um erro ao processar sua mensagem." };
        setMessages((prevMessages) => [...prevMessages, errorMessage]);
        setDigitando(false);
      });
  };

  // const handleDownloadReport = () => {
  //   // Logic to download the report
  //   console.log("Downloading report...");
  // };

  const handleCleanLocalSStora = () => {
    localStorage.removeItem("id");
    window.location.reload();
  };


  return (
    <div className="flex h-screen">
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        <div className="flex-1 overflow-hidden">
          <ScrollArea className="h-full">
            {!hasChatStarted ? (
              // Initial UI before the chat starts
              <div className="flex flex-col h-full items-center justify-center">
                <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-400 to-accent w-fit bg-clip-text text-transparent mb-4">
                  Olá, Gestor
                </h1>
                <h2 className="text-4xl text-secondary mb-12">
                  Como posso te ajudar?
                </h2>
                <div className="grid grid-cols-2 gap-6 w-full max-w-2xl px-4">
                  {/* Example Buttons */}
                  <Button variant="outline" size="lg" className="h-32 text-lg flex flex-col items-center justify-center" onClick={handleSendMessage}>
                    <BarChart className="h-8 w-8 mb-2" />
                    Analise o clima de BH
                  </Button>
                  <Button variant="outline" size="lg" className="h-32 text-lg flex flex-col items-center justify-center" onClick={handleSendMessage}>
                    <FileText className="h-8 w-8 mb-2" />
                    Crie report da cidade Jau
                  </Button>
                  <Button variant="outline" size="lg" className="h-32 text-lg flex flex-col items-center justify-center" onClick={handleSendMessage}>
                    <Type className="h-8 w-8 mb-2" />
                    Índice de poluição de Florianópolis
                  </Button>
                  <Button variant="outline" size="lg" className="h-32 text-lg flex flex-col items-center justify-center" onClick={handleSendMessage}>
                    <Languages className="h-8 w-8 mb-2" />
                    Principais problemas climáticos de SP 
                  </Button>
                </div>
              </div>
            ) : (
              // Chat Messages Area
              <div className="p-4 space-y-4">
                {
                  cities?(
                <div key={0} 
                    className={`p-3 rounded-lg shadow bg-blue-100}`}>
                    <p className="font-semibold">AI:</p>
                    <p>Ola gestor climático da cidade de {cities}. Como posso ajuda-lo hoje?</p>
                  </div>
                  ):(
                    <></>
                  )
                }
                {messages.map((msg, index) => (

                  <div 
                    key={index} 
                    className={`p-3 rounded-lg shadow ${
                      msg.sender === "AI" ? "bg-white" : "bg-blue-100"
                    }`}
                  >
                    <p className="font-semibold">{msg.sender}:</p>
                    <p>{msg.text}</p>
                  </div>
                ))}
                {digitando && (
                  <div className="p-3 bg-white rounded-lg shadow">
                    <p className="font-semibold">AI:</p>
                    <p>Digitando...</p>
                  </div>
                )}
              </div>
            )}
          </ScrollArea>
        </div>
        {/* Input Area */}
        <div className="p-4 bg-white border-t">
          <div className="flex space-x-2">
            <Input 
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  handleSendMessage();
                }
              }}
              placeholder="Digite sua mensagem aqui..." 
              className="flex-1" 
            />
            <Button size="lg" onClick={handleSendMessage} disabled={digitando}>
              <MessageSquare className="h-5 w-5 mr-2" />
              Enviar
            </Button>
          </div>
        </div>
      </div>
      {/* KPI Panel */}
      <div
        className={`${
          isKpiOpen ? "w-80" : "w-0"
        } transition-all duration-300 bg-white border-l overflow-hidden`}
      >
        {isKpiOpen && (
          <div className="p-6">
            <div className="flex justify-between items-center mb-6">
              <h1 className="text-3xl font-semibold">{cities}</h1>
              <Button variant="ghost" size="icon" onClick={toggleKpi}>
                <X className="h-5 w-5" />
              </Button>
            </div>
            <div>
              <Button variant="outline" size="lg" className="w-full mb-4" onClick={handleCleanLocalSStora}>Alterar Município</Button>
              {/* <button onClick={handleCleanLocalSStora} className="" >Mudar cidade</button> */}
            </div>
            <div className="pb-6 border-b border-gray-200">
              <h2 className="text-xl font-bold tracking-wide text-gray-600">Principais Indicadores</h2>
            </div>
            <div className="space-y-6 pt-6">
              {/* KPI Cards */}
              {key_indicators.map((item, index) => (
                <div key={index} className="bg-gray-100 p-5 rounded-lg shadow-sm">
                  <h3 className="font-semibold text-m text-gray-500 mb-1">{index + 1} Índice</h3>
                  <p className="text-l font-extrabold text-gray-900">{item.content}</p>
                </div>
              ))}
              {/* Download Button */}
              {/* <Button 
                variant="outline" 
                size="lg" 
                className="w-full flex items-center justify-center mt-4"
                onClick={handleDownloadReport}
              >
                <Download className="h-5 w-5 mr-2" />
                Baixar Relatório Completo
              </Button> */}
            </div>
          </div>
        )}
      </div>
      {/* KPI Toggle Button */}
      {!isKpiOpen && (
        <Button
          variant="outline"
          size="icon"
          className="fixed right-4 top-4"
          onClick={toggleKpi}
        >
          <BarChart2 className="h-4 w-4" />
        </Button>
      )}
    </div>
  );
}

export default Chat;

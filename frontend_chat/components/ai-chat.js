'use client'

import { useEffect, useState } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { MessageSquare, BarChart2, X, BarChart, FileText, Type, Languages, Leaf } from "lucide-react"

export default function ClimateAssistant() {
  const [isKpiOpen, setIsKpiOpen] = useState(true)
  const [hasChatStarted, setHasChatStarted] = useState(true)
  const [digitando, setDigitando] = useState(false)
  const [id, setId] = useState(localStorage.getItem("id"))
  const [cities, setCities] = useState([])
  const [key_indicators, setKey_indicators] = useState([])
  const [prompt, setPrompt] = useState("")
  const [messages, setMessages] = useState([])

  useEffect(() => {
    if (id) {
      fetch(`http://localhost:8000/chat/${id}`)
        .then((response) => response.json())
        .then((data) => {
          console.log(data)
          setCities(data.city)
          setKey_indicators(data.key_indicators)
        })
    }
  }, [id])

  console.log(messages)

  const toggleKpi = () => setIsKpiOpen(!isKpiOpen)

  const handleSendMessage = () => {
    if (prompt.trim() === "") return
    const userMessage = { sender: "Você", text: prompt }
    setMessages((prevMessages) => [...prevMessages, userMessage])
    setPrompt("")
    setDigitando(true)
    sendPrompt(prompt)
  }

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
        console.log(data)
        const aiMessage = { sender: "AI", text: data.response }
        setMessages((prevMessages) => [...prevMessages, aiMessage])
        setDigitando(false)
      })
      .catch((error) => {
        console.error(error)
        const errorMessage = { sender: "AI", text: "Desculpe, ocorreu um erro ao processar sua mensagem." }
        setMessages((prevMessages) => [...prevMessages, errorMessage])
        setDigitando(false)
      })
  }

  const handleCleanLocalStorage = () => {
    localStorage.removeItem("id")
    window.location.reload()
  }

  return (
    <div className="flex flex-col h-screen bg-background text-foreground">
      {/* Minimalistic Header */}
      <header className="bg-background border-b border-border p-4">
        <div className="container mx-auto flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <Leaf className="h-7 w-7 text-green-800" />
            <h1 className="text-2xl font-semibold text-green-800">Climate AI</h1>

          </div>
          {cities && (
            <div className="text-sm font-medium text-muted-foreground">
              {cities}
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Chat Area */}
        <div className="flex-1 flex flex-col">
          <ScrollArea className="flex-1 p-4">
            {!hasChatStarted ? (
              <div className="flex flex-col h-full items-center justify-center">
                <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent mb-4">
                  Olá, Gestor
                </h1>
                <h2 className="text-2xl text-muted-foreground mb-8">
                  Como posso te ajudar?
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-2xl">
                  <Button variant="outline" className="h-24 text-sm flex flex-col items-center justify-center" onClick={() => { setHasChatStarted(true); handleSendMessage(); }}>
                    <BarChart className="h-6 w-6 mb-2" />
                    Analise o clima de BH
                  </Button>
                  <Button variant="outline" className="h-24 text-sm flex flex-col items-center justify-center" onClick={() => { setHasChatStarted(true); handleSendMessage(); }}>
                    <FileText className="h-6 w-6 mb-2" />
                    Crie report da cidade Jau
                  </Button>
                  <Button variant="outline" className="h-24 text-sm flex flex-col items-center justify-center" onClick={() => { setHasChatStarted(true); handleSendMessage(); }}>
                    <Type className="h-6 w-6 mb-2" />
                    Índice de poluição de Florianópolis
                  </Button>
                  <Button variant="outline" className="h-24 text-sm flex flex-col items-center justify-center" onClick={() => { setHasChatStarted(true); handleSendMessage(); }}>
                    <Languages className="h-6 w-6 mb-2" />
                    Principais problemas climáticos de SP
                  </Button>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {cities && (
                  <div className="flex justify-start">
                    <div className="max-w-[80%] p-3 rounded-lg bg-green-800/15 text-secondary-foreground">
                      <p className="font-medium mb-1">AI</p>
                      <p>Olá gestor climático da cidade de {cities}. Como posso ajudá-lo hoje?</p>
                    </div>
                  </div>
                )}
                {messages.map((msg, index) => (
                  <div key={index} className={`flex ${msg.sender === "AI" ? "justify-start" : "justify-end"}`}>
                    <div className={`max-w-[80%] p-3 rounded-lg ${msg.sender === "AI" ? "bg-green-800/15 text-secondary-foreground" : "bg-primary text-primary-foreground"}`}>
                      <p className="font-medium mb-1">{msg.sender}</p>
                      {msg.sender === "AI" ? (
                        <div dangerouslySetInnerHTML={{ __html: msg.text }} />
                      ) : (
                        <p>{msg.text}</p>
                      )}
                    </div>
                  </div>
                ))}
                {digitando && (
                  <div className="flex justify-start">
                    <div className="max-w-[80%] p-3 rounded-lg bg-secondary text-secondary-foreground">
                      <p className="font-medium mb-1">AI</p>
                      <p>Digitando...</p>
                    </div>
                  </div>
                )}
              </div>
            )}
          </ScrollArea>
          {/* Input Area */}
          <div className="p-4 bg-background border-t border-border">
            <div className="flex space-x-2">
              <Input
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleSendMessage()
                  }
                }}
                placeholder="Digite sua mensagem aqui..."
                className="flex-1"
              />
              <Button onClick={handleSendMessage} disabled={digitando}>
                <MessageSquare className="h-5 w-5 mr-2" />
                Enviar
              </Button>
            </div>
          </div>
        </div>

        {/* KPI Panel */}
        <div className={`${isKpiOpen ? "w-80" : "w-0"} transition-all duration-300 bg-background border-l border-border overflow-hidden`}>
          {isKpiOpen && (
            <div className="h-full flex flex-col">
              <div className="p-4 border-b border-border">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-xl font-semibold">{cities}</h2>
                  <Button variant="ghost" 
                          size="icon" 
                          className="hover:bg-green-800 hover:text-white transition-colors duration-200" 
                          onClick={toggleKpi}>
                    <X className="h-4 w-3 " />
                  </Button>
                </div>
                <Button 
                  variant="outline" 
                  size="medium" 
                  className="w-full bg-white text-green-800 hover:bg-green-800 hover:text-white transition-colors duration-200" 
                  onClick={handleCleanLocalStorage}
                >
                  Alterar Município
                </Button>
              </div>
              <ScrollArea className="flex-1 p-4">
                <h3 className="text-sm font-medium text-muted-foreground mb-2">Desafios climáticos:</h3>
                <div className="space-y-2">
                  {key_indicators.map((item, index) => (
                    <div key={index} className="bg-secondary/50 p-3 rounded-md">
                      <h4 className="text-xs font-medium text-muted-foreground mb-1">{index + 1} Índice</h4>
                      <p className="text-xl font-medium">{item.content}</p>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </div>
          )}
        </div>
      </div>

      {/* KPI Toggle Button */}
      {!isKpiOpen && (
        <Button
          variant="outline"
          size="icon"
          className="fixed right-4 top-16"
          onClick={toggleKpi}
        >
          <BarChart2 className="h-4 w-4" />
        </Button>
      )}
    </div>
  )
}
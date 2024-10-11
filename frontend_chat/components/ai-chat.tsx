"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MessageSquare, BarChart2, X, BarChart, FileText, Type, Languages, Download } from "lucide-react";
import { useState } from "react";

export default function Chat() {
  const [isKpiOpen, setIsKpiOpen] = useState(true);
  const [hasChatStarted, setHasChatStarted] = useState(false);

  const toggleKpi = () => setIsKpiOpen(!isKpiOpen);

  const handleSendMessage = () => {
    setHasChatStarted(true);
    // Add logic here to handle sending the message
  };

  const handleDownloadReport = () => {
    // Add logic here to handle downloading the report
    console.log("Downloading report...");
  };

  return (
    <div className="flex h-screen">
      <div className="flex-1 flex flex-col">
        <div className="flex-1 overflow-hidden">
          <ScrollArea className="h-full">
            {!hasChatStarted ? (
              <div className="flex flex-col h-full items-center justify-center">
                <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-400 to-accent w-fit bg-clip-text text-transparent mb-4">
                  Olá, Gestor
                </h1>
                <h2 className="text-4xl text-secondary mb-12">
                  Como posso te ajudar?
                </h2>
                <div className="grid grid-cols-2 gap-6 w-full max-w-2xl px-4">
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
                  Índice de poluição de Florianopolis
                  </Button>
                  <Button variant="outline" size="lg" className="h-32 text-lg flex flex-col items-center justify-center" onClick={handleSendMessage}>
                    <Languages className="h-8 w-8 mb-2" />
                    Principais problemas climáticos de SP 
                  </Button>
                </div>
              </div>
            ) : (
              <div className="p-4 space-y-4">
                <div className="bg-white p-3 rounded-lg shadow">
                  <p className="font-semibold">AI:</p>
                  <p>Hello! How can I assist you today?</p>
                </div>
                <div className="bg-blue-100 p-3 rounded-lg shadow">
                  <p className="font-semibold">You:</p>
                  <p>Can you help me with a data analysis task?</p>
                </div>
                <div className="bg-white p-3 rounded-lg shadow">
                  <p className="font-semibold">AI:</p>
                  <p>
                    I'd be happy to help you with your data analysis task. Could
                    you please provide more details about the specific analysis
                    you need to perform? For example, what kind of data are you
                    working with, and what insights are you looking to gain?
                  </p>
                </div>
              </div>
            )}
          </ScrollArea>
        </div>
        <div className="p-4 bg-white border-t">
          <div className="flex space-x-2">
            <Input placeholder="Type your message here..." className="flex-1" />
            <Button size="lg" onClick={handleSendMessage}>
              <MessageSquare className="h-5 w-5 mr-2" />
              Send
            </Button>
          </div>
        </div>
      </div>
      <div
        className={`${
          isKpiOpen ? "w-80" : "w-0"
        } transition-all duration-300 bg-white border-l overflow-hidden`}
      >
          {isKpiOpen && (
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h1 className="text-4xl font-semibold">Bauru</h1>
                <Button variant="ghost" size="icon" onClick={toggleKpi}>
                  <X className="h-5 w-5" />
                </Button>
              </div>
              <div className="pb-6 border-b border-gray-200">
                <h2 className="text-xl font-bold tracking-wide text-gray-600">KPIs & Artifacts</h2>
              </div>
              <div className="space-y-6 pt-6">
                {/* KPI Cards */}
                <div className="bg-gray-100 p-5 rounded-lg shadow-sm">
                  <h3 className="font-semibold text-lg text-gray-500 mb-1">1 Índice</h3>
                  <p className="text-xl font-extrabold text-gray-900">Clima Seca</p>
                </div>
                <div className="bg-gray-100 p-5 rounded-lg shadow-sm">
                  <h3 className="font-semibold text-lg text-gray-500 mb-1">2 Índice</h3>
                  <p className="text-xl font-extrabold text-gray-900">Emissão de gás carbonico alto</p>
                </div>
                <div className="bg-gray-100 p-5 rounded-lg shadow-sm">
                  <h3 className="font-semibold text-lg text-gray-500 mb-1">3 Índice</h3>
                  <p className="text-xl font-extrabold text-gray-900">Lixo produzido</p>
                </div>
                {/* List Section */}
                
                {/* Download Button */}
                <Button 
                  variant="outline" 
                  size="lg" 
                  className="w-full flex items-center justify-center mt-4"
                  onClick={handleDownloadReport}
                >
                  <Download className="h-5 w-5 mr-2" />
                  Download Full Report
                </Button>
              </div>
            </div>
          )}
        </div>
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
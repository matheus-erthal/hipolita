"use client"
import { Loader2, CircleHelp } from "lucide-react"

import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox"
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle
} from "@/components/ui/dialog"

import { useState } from 'react'

export default function Home() {
  
  const [currentStep, setCurrentStep] = useState(0)
  const [loading, setLoading] = useState(false)
  const [searchTerms, setSearchTerms] = useState("")
  const [openDescription, setOpenDescription] = useState(false)
  const [currentDataset, setCurrentDataset] = useState("")
  const [datasets, setDatasets] = useState([])
  const [columns, setColumns] = useState([])
  const [dimension, setDimension] = useState("")
  const [metric, setMetric] = useState("")
  const [resultImage, setResultImage] = useState("")
  const [openExplanation, setOpenExplanation] = useState(false)

  const handleSearchTerms = async () => {
    setLoading(true);
    try {
      const resp = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/get_datasets?tags_final=${searchTerms}`);
      const data = await resp.json();
      setDatasets(JSON.parse(data)["data"]);
      setCurrentStep(1);
    } catch (e) {
      console.error(e)
    }
    setLoading(false);
  }

  const handleSeeDescription = (dataset : any) => {
    setCurrentDataset(dataset);
    setOpenDescription(true);
  }

  function truncateString(str:string, num:number, dataset:any) {
    if (str && str.length > num) {
      const descricao = str.slice(0, num) + "... ";
      return (
        <>        
          <p>{descricao}</p>
          <a onClick={() => handleSeeDescription(dataset)}>Ver mais</a>
        </>
      );
    } else {
      return str;
    }
  }

  const handleDatasetSelection = async (dataset : any) => {
    setLoading(true);
    try {
      const resp = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/select_dataset?selected_url=${encodeURI(dataset[2])}`);
      const data = await resp.json();
      setColumns(data);
      setCurrentDataset(dataset);
      setCurrentStep(2);
    } catch (e) {
      console.error(e)
      alert("Erro ao selecionar o conjunto de dados. Por favor, escolha outro")
    }
    setLoading(false);
  }

  const handleColumnSelection = async () => {
    setLoading(true);
    if(dimension == "" || metric == "") {
      alert("Por favor, selecione uma dimensão e uma métrica na tabela abaixo")
      setLoading(false);
      return;
    }
    try {
      const resp = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/select_columns?selected_url=${encodeURI(currentDataset[2])}&dimension=${dimension}&metric=${metric}`);
      const resultBlob = await resp.blob();
      const resultObjectURL = URL.createObjectURL(resultBlob);
      setResultImage(resultObjectURL);
      setCurrentStep(3);
    } catch (e) {
      console.error(e)
      alert("Erro ao analisar os dados. Por favor, tente novamente")
    }
    setLoading(false);
  }

  const handleBackToStart = () => {
    setCurrentStep(0);
    setSearchTerms("");
    setDatasets([]);
    setColumns([]);
    setDimension("");
    setMetric("");
    setResultImage("");
  }

  const renderStep = () => {
    switch (currentStep) {
      case 0:
        return renderSearchTermsInput();
      case 1:
        return renderDatasets();
      case 2:
        return renderColumns();
      case 3:
        return renderResults();
      default:
        return null;
    }
  }

  const renderSearchTermsInput = () => {
    return (
      <>
        <h2 className="mb-4">Digite os termos para serem buscados nos dados abertos governamentais:</h2>
        <Input className="mb-4" value={searchTerms} onChange={(e) => setSearchTerms(e.target.value)} />
        <Button className="mb-4" disabled={loading} onClick={() => handleSearchTerms()}>
          {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          {loading ? "Carregando..." : "Buscar"}
        </Button>
      </>
    );
  }

  const renderDatasets = () => {
    return (
      <>
      <Table>
        <TableCaption>Os conjuntos de dados encontrados</TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[100px]">ID</TableHead>
            <TableHead>Nome</TableHead>
            <TableHead>Descrição</TableHead>
            <TableHead></TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {datasets.map((dataset, index) => (
            <TableRow key={index}>
              <TableCell className="font-medium">{dataset[0]}</TableCell>
              <TableCell>{dataset[1]}</TableCell>
              <TableCell>{truncateString(dataset[4], 150, dataset)}</TableCell>
              <TableCell><Button onClick={() => handleDatasetSelection(dataset)}>Escolher</Button></TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <Dialog open={openDescription} onOpenChange={setOpenDescription}>
        <DialogContent className="max-h-80 overflow-y-auto p-10">
          <DialogHeader>
            <DialogTitle>{currentDataset[1]}</DialogTitle>
            <DialogDescription>{currentDataset[4]}</DialogDescription>
          </DialogHeader>
        </DialogContent>
      </Dialog>
      </>
    );
  }

  const renderColumns = () => {
    return (
      <>
      <div className="mb-6">
        <h2><strong>Título:</strong> {currentDataset[1]}</h2>
        <p><strong>Descrição: </strong> {currentDataset[4]}</p>
        <p><strong>Origem dos dados:</strong> <a href={currentDataset[2]} target="_blank" className="underline">Link para o conjunto de dados</a></p>
      </div>
      <Button className="mb-4" onClick={() => handleColumnSelection()}>Analisar</Button>
      <div className="my-12">
        <p>Agora, você precisa escolher, dentro dos conjunto de dados selecionados, como você quer visualizar essas informações</p>
        <br/>
        <p><strong>Dimensão:</strong> São as categorias que usamos para organizar coisas, como &quot;animais&quot;, &quot;cores&quot; ou &quot;dias da semana&quot;.</p>
        <br/>
        <p><strong>Métrica:</strong> São os números que contamos, como &quot;quantos brinquedos&quot;, &quot;quantas maçãs&quot; ou &quot;quantos dias&quot;.</p>
      </div>
      <Table>
        <TableCaption>Dimensões ajudam a agrupar, e métricas mostram quantidades</TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead className="text-center">Dimensão</TableHead>
            <TableHead className="text-center">Métrica</TableHead>
            <TableHead className="text-center">Nome da Coluna</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {columns.map((column, index) => (
            <TableRow key={index}>
              <TableCell>
                <Checkbox 
                  checked={dimension == column}
                  onCheckedChange={(checked) => {
                    if(checked) {
                      if(column == metric) {
                        alert("Dimensão não pode ser igual a métrica")
                      } else {
                        setDimension(column)
                      }
                    } else setDimension("")
                  }}
                />
              </TableCell>
              <TableCell>
              <Checkbox 
                  checked={metric == column}
                  onCheckedChange={(checked) => {
                    if(checked) {
                      if(column == dimension) {
                        alert("Métrica não pode ser igual a dimensão")
                      } else {
                        setMetric(column)
                      }
                    } else setMetric("")
                  }}
                />
              </TableCell>
              <TableCell>{column}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <Dialog open={openExplanation} onOpenChange={setOpenExplanation}>
        <DialogContent className="max-h-80 overflow-y-auto p-10">
          <DialogHeader>
            <DialogTitle>O que são dimensões e métricas?</DialogTitle>
            <DialogDescription>
              <br/>
              <p><strong>Dimensão:</strong> São as categorias que usamos para organizar coisas, como &quot;animais&quot;, &quot;cores&quot; ou &quot;dias da semana&quot;.</p>
              <br/>
              <p><strong>Métrica:</strong> São os números que contamos, como &quot;quantos brinquedos&quot;, &quot;quantas maçãs&quot; ou &quot;quantos dias&quot;.</p>
            </DialogDescription>
          </DialogHeader>
        </DialogContent>
      </Dialog>
      </>
    );
  }

  const renderResults = () => {
    return (
      <>
      <h2>Resultado:</h2>
      <img src={resultImage} />
      <div className="mt-4 flex-row justify-between">
      <Button className="m-2" variant="outline" onClick={() => setCurrentStep(0)}>Voltar para o início</Button>
      <Button className="m-2" onClick={() => window.location.href = "https://forms.gle/jgdCBoeyF6zqV2Er5"}>Responder pesquisa</Button>
      </div>
      </>
    );
  }

  return (
    <main className="flex min-h-screen flex-col items-center p-2">
      <div className="self-start">
        {currentStep != 0 && <Button className="m-2" variant={"outline"} onClick={() => handleBackToStart()}>Voltar para o início</Button>}
        {/* {currentStep != 0 && <Button className="m-2" variant={"secondary"} onClick={() => setCurrentStep(currentStep - 1)}>Voltar uma etapa</Button>} */}
      </div>
      <div>
        <img src="icon.png" className="w-40 h-40"></img>
        <h1 className="text-4xl font-bold mb-10 text-center">Hipólita</h1>
      </div>
      <div className="z-10 w-full max-w-5xl flex-col items-center justify-between font-mono text-sm lg:flex text-center">
        {renderStep()}
      </div>
    </main>
  );
}

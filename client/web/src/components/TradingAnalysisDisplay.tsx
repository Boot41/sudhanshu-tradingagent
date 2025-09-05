import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  TrendingUp, TrendingDown, Minus, 
  BarChart3, Brain, Users, Target,
  Clock, CheckCircle, AlertCircle
} from "lucide-react";

interface AnalystScores {
  fundamentals: number;
  technical: number;
  sentiment: number;
  news: number;
}

interface ResearchAssessment {
  bull_score: number;
  bear_score: number;
  net_score: number;
  stance: string;
  confidence: number;
}

interface TradingDecision {
  action: string;
  position_size: number;
  rationale: string;
  risk_metrics: Record<string, any>;
}

interface TradingAnalysisData {
  workflow_id: string;
  ticker: string;
  company_name: string;
  analysis_timestamp: string;
  workflow_status: string;
  analyst_scores: AnalystScores;
  research_assessment: ResearchAssessment;
  trading_decision: TradingDecision;
  executive_summary: string;
  processing_time_ms: number;
}

interface TradingAnalysisDisplayProps {
  data: TradingAnalysisData;
}

export const TradingAnalysisDisplay: React.FC<TradingAnalysisDisplayProps> = ({ data }) => {
  const getActionColor = (action: string) => {
    switch (action.toUpperCase()) {
      case 'BUY': return 'text-green-600 bg-green-50 border-green-200';
      case 'SELL': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    }
  };

  const getActionIcon = (action: string) => {
    switch (action.toUpperCase()) {
      case 'BUY': return <TrendingUp className="h-4 w-4" />;
      case 'SELL': return <TrendingDown className="h-4 w-4" />;
      default: return <Minus className="h-4 w-4" />;
    }
  };

  const getStanceColor = (stance: string) => {
    switch (stance.toLowerCase()) {
      case 'bullish': return 'text-green-600 bg-white border-green-200';
      case 'bearish': return 'text-red-600 bg-white border-red-200';
      default: return 'text-black bg-white border-gray-200';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 70) return 'text-green-600';
    if (score >= 40) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header Card */}
      <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-2xl font-bold text-blue-900">
                {data.ticker} - {data.company_name}
              </CardTitle>
              <p className="text-blue-700 mt-1">Trading Analysis Report</p>
            </div>
            <div className="text-right">
              <div className="flex items-center gap-2 text-sm text-blue-600">
                <Clock className="h-4 w-4" />
                {data.processing_time_ms.toFixed(0)}ms
              </div>
              <div className="flex items-center gap-2 text-sm text-green-600 mt-1">
                <CheckCircle className="h-4 w-4" />
                {data.workflow_status}
              </div>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Trading Decision Card */}
      <Card className="border-2 border-primary/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5 text-primary" />
            Trading Recommendation
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Badge className={`px-4 py-2 text-lg font-bold ${getActionColor(data.trading_decision.action)}`}>
                {getActionIcon(data.trading_decision.action)}
                {data.trading_decision.action}
              </Badge>
              {data.trading_decision.action !== 'HOLD' && (
                <div className="text-lg font-semibold">
                  {data.trading_decision.position_size.toFixed(1)}% Allocation
                </div>
              )}
            </div>
            <div className="text-right">
              <div className="text-sm text-muted-foreground">Net Score</div>
              <div className={`text-2xl font-bold ${getScoreColor(data.research_assessment.net_score + 50)}`}>
                {data.research_assessment.net_score.toFixed(1)}
              </div>
            </div>
          </div>
          
          <div className="bg-muted/30 p-4 rounded-lg">
            <h4 className="font-semibold mb-2">Rationale</h4>
            <p className="text-sm text-muted-foreground">{data.trading_decision.rationale}</p>
          </div>
        </CardContent>
      </Card>

      {/* Analyst Scores Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {Object.entries(data.analyst_scores).map(([key, score]) => (
          <Card key={key} className="text-center">
            <CardContent className="pt-6">
              <div className="space-y-3">
                <div className="flex justify-center">
                  <BarChart3 className="h-8 w-8 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold capitalize">{key}</h3>
                  <div className={`text-2xl font-bold ${getScoreColor(score)}`}>
                    {score.toFixed(1)}
                  </div>
                </div>
                <Progress value={score} className="h-2" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Research Assessment */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5 text-primary" />
            Research Assessment
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-sm text-muted-foreground mb-1">Bull Score</div>
              <div className="text-2xl font-bold text-green-600">
                {data.research_assessment.bull_score.toFixed(1)}
              </div>
              <Progress value={data.research_assessment.bull_score} className="h-2 mt-2" />
            </div>
            
            <div className="text-center">
              <div className="text-sm text-muted-foreground mb-1">Bear Score</div>
              <div className="text-2xl font-bold text-red-600">
                {data.research_assessment.bear_score.toFixed(1)}
              </div>
              <Progress value={data.research_assessment.bear_score} className="h-2 mt-2" />
            </div>
            
            <div className="text-center">
              <div className="text-sm text-muted-foreground mb-1">Confidence</div>
              <div className="text-2xl font-bold text-blue-600">
                {data.research_assessment.confidence.toFixed(1)}%
              </div>
              <Progress value={data.research_assessment.confidence} className="h-2 mt-2" />
            </div>
          </div>
          
          <div className="mt-6 text-center">
            <Badge className={`px-4 py-2 text-lg ${getStanceColor(data.research_assessment.stance)}`}>
              Overall Stance: {data.research_assessment.stance.toUpperCase()}
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Executive Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-primary" />
            Executive Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground leading-relaxed">
            {data.executive_summary}
          </p>
        </CardContent>
      </Card>

      {/* Workflow Details */}
      <Card className="bg-muted/20">
        <CardHeader>
          <CardTitle className="text-sm text-muted-foreground">Analysis Details</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <div className="text-muted-foreground">Workflow ID</div>
              <div className="font-mono text-xs">{data.workflow_id}</div>
            </div>
            <div>
              <div className="text-muted-foreground">Timestamp</div>
              <div className="font-mono text-xs">
                {new Date(data.analysis_timestamp).toLocaleString()}
              </div>
            </div>
            <div>
              <div className="text-muted-foreground">Processing Time</div>
              <div className="font-mono text-xs">{data.processing_time_ms.toFixed(0)}ms</div>
            </div>
            <div>
              <div className="text-muted-foreground">Status</div>
              <div className="font-mono text-xs capitalize">{data.workflow_status}</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

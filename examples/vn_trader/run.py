# flake8: noqa
from vnpy.event import EventEngine, Event

from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import MainWindow, create_qapp

from vnpy_ctp import CtpGateway
# from vnpy_ctptest import CtptestGateway
# from vnpy_mini import MiniGateway
# from vnpy_femas import FemasGateway
# from vnpy_sopt import SoptGateway
# from vnpy_sec import SecGateway
# from vnpy_uft import UftGateway
# from vnpy_esunny import EsunnyGateway
# from vnpy_xtp import XtpGateway
# from vnpy_tora import ToraStockGateway
# from vnpy_tora import ToraOptionGateway
# from vnpy_comstar import ComstarGateway
# from vnpy_ib import IbGateway
# from vnpy_tap import TapGateway
# from vnpy_da import DaGateway
# from vnpy_rohon import RohonGateway
# from vnpy_tts import TtsGateway
# from vnpy_ost import OstGateway
# from vnpy_hft import GtjaGateway

from vnpy_ctastrategy import CtaStrategyApp  # CTA策略引擎
from vnpy_ctabacktester import CtaBacktesterApp  # CTA策略回测
# from vnpy_spreadtrading import SpreadTradingApp  # 价差套利交易
# from vnpy_algotrading import AlgoTradingApp  # 算法交易
# from vnpy_optionmaster import OptionMasterApp  # 期权波动率交易
from vnpy_portfoliostrategy import PortfolioStrategyApp  # 多合约组合策略
# from vnpy_scripttrader import ScriptTraderApp  # 脚本策略
# from vnpy_chartwizard import ChartWizardApp  # K线图表
# from vnpy_rpcservice import RpcServiceApp  # RPC服务
# from vnpy_excelrtd import ExcelRtdApp  # ExcelRTD
from vnpy_datamanager import DataManagerApp  # 历史数据管理
# from vnpy_datarecorder import DataRecorderApp  # 行情记录
from vnpy_riskmanager import RiskManagerApp  # 风险管理
# from vnpy_webtrader import WebTraderApp  # Web服务
# from vnpy_portfoliomanager import PortfolioManagerApp  # 投资组合管理
# from vnpy_paperaccount import PaperAccountApp  # 本地模拟交易

from 数据服务接口 import register as DataMsgRegister  # 数据中心推送


def main():
    """"""
    qapp = create_qapp()

    event_engine = EventEngine()

    main_engine = MainEngine(event_engine)

    main_engine.add_gateway(CtpGateway)
    # main_engine.add_gateway(CtptestGateway)
    # main_engine.add_gateway(MiniGateway)
    # main_engine.add_gateway(FemasGateway)
    # main_engine.add_gateway(SoptGateway)
    # main_engine.add_gateway(SecGateway)    
    # main_engine.add_gateway(UftGateway)
    # main_engine.add_gateway(EsunnyGateway)
    # main_engine.add_gateway(XtpGateway)
    # main_engine.add_gateway(ToraStockGateway)
    # main_engine.add_gateway(ToraOptionGateway)
    # main_engine.add_gateway(ComstarGateway)
    # main_engine.add_gateway(IbGateway)
    # main_engine.add_gateway(TapGateway)
    # main_engine.add_gateway(DaGateway)
    # main_engine.add_gateway(RohonGateway)
    # main_engine.add_gateway(TtsGateway)
    # main_engine.add_gateway(OstGateway)
    # main_engine.add_gateway(NhFuturesGateway)
    # main_engine.add_gateway(NhStockGateway)

    # main_engine.add_app(PaperAccountApp)  # 本地模拟交易
    main_engine.add_app(CtaStrategyApp)  # CTA策略引擎
    main_engine.add_app(CtaBacktesterApp)  # CTA策略回测
    # main_engine.add_app(SpreadTradingApp)  # 价差套利交易
    # main_engine.add_app(AlgoTradingApp)  # 算法交易
    # main_engine.add_app(OptionMasterApp)  # 期权波动率交易
    main_engine.add_app(PortfolioStrategyApp)  # 多合约组合策略
    # main_engine.add_app(ScriptTraderApp)  # 脚本策略
    # main_engine.add_app(ChartWizardApp)  # K线图表
    # main_engine.add_app(RpcServiceApp)  # RPC服务
    # main_engine.add_app(ExcelRtdApp)  # ExcelRTD
    main_engine.add_app(DataManagerApp)  # 历史数据管理
    # main_engine.add_app(DataRecorderApp)  # 行情记录
    main_engine.add_app(RiskManagerApp)  # 风险管理
    # main_engine.add_app(WebTraderApp)  # Web服务
    # main_engine.add_app(PortfolioManagerApp)  # 投资组合管理

    def DataMsgCallBack(MsgTime):
        event = Event('eDataMsg', MsgTime)
        main_engine.event_engine.put(event)

    DataMsgRegister(DataMsgCallBack, minute=True)  # 注册数据中心推送

    main_window = MainWindow(main_engine, event_engine)
    main_window.showMaximized()

    qapp.exec()


if __name__ == "__main__":
    main()

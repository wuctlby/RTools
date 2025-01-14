import sys
import ROOT
import argparse
sys.path.append('../')  
from utils.Load import load_histos

# axis
bdt_sig = 5
bdt_bkg = 4
axis_pt = 1
# nCutSets
nCutSets = 5
# cutSets
cutMins = [0.05, 0.27, 0.4, 0.67, 0.87]
cutMaxs = [0.25, 0.45, 0.65, 0.85, 1.0]

def main(inputFile):

    # # 加载包含直方图的ROOT文件
    # f = ROOT.TFile.Open("myfile.root")
    # h = f.Get("h1")  # 替换为实际的直方图名称
    
    inFile = ROOT.TFile(inputFile)
    thn = inFile.Get("hf-task-flow-charm-hadrons/hSparseFlowCharm")
    
    thn.GetAxis(axis_pt).SetRangeUser(2, 3)
    thn.GetAxis(bdt_bkg).SetRangeUser(0, 0.001)
    
    fdDistr = thn.Projection(bdt_sig)
    fdDistr.Draw()
    input("Press Enter to continue...")
    fdDistr.SetDirectory(0)

    # 获取bin的低边界、高边界和内容
    n_bins = fdDistr.GetNbinsX()
    bin_low_edges = [fdDistr.GetXaxis().GetBinLowEdge(i) for i in range(1, n_bins+1)]
    bin_high_edges = [fdDistr.GetXaxis().GetBinUpEdge(i) for i in range(1, n_bins+1)]
    bin_contents = [fdDistr.GetBinContent(i) for i in range(1, n_bins+1)]

    # 设置划分的区间数
    n = 7  # 指定的区间数

    # 计算总数
    total = sum(bin_contents)

    # 获取最后一个bin的内容
    last_bin_content = bin_contents[-1]

    # 计算阈值
    threshold = total / n

    if last_bin_content > threshold:
        # 划分成n-1个区间，不包括最后一个bin
        remaining_contents = bin_contents[:-1]
        remaining_low_edges = bin_low_edges[:-1]
        remaining_high_edges = bin_high_edges[:-1]
        remaining_total = total - last_bin_content

        # 计算剩余bin的累积概率
        remaining_cumulative = []
        s = 0.0
        for content in remaining_contents:
            s += content
            remaining_cumulative.append(s / remaining_total)

        # 计算目标累积概率
        target_cdfs = [i / (n - 1) for i in range(1, n)]

        # 找到划分点
        division_points = []
        for cdf in target_cdfs:
            # 找到最小的j，使得remaining_cumulative[j] >= cdf
            j = next(j for j, val in enumerate(remaining_cumulative) if val >= cdf)
            # 线性插值
            if j == 0:
                x = remaining_low_edges[0]
            else:
                frac = (cdf - remaining_cumulative[j - 1]) / (remaining_cumulative[j] - remaining_cumulative[j - 1])
                x = remaining_low_edges[j] + frac * (remaining_high_edges[j] - remaining_low_edges[j])
            division_points.append(x)

        # 输出n-1个区间
        intervals = []
        current_low = remaining_low_edges[0]
        for point in division_points[:-1]:
            intervals.append((current_low, point))
            current_low = point
        intervals.append((current_low, remaining_high_edges[-1]))

        # 再加上最后一个bin作为一个区间
        intervals.append((bin_low_edges[-1], bin_high_edges[-1]))
    else:
        # 计算所有bin的累积概率
        cumulative = []
        s = 0.0
        for content in bin_contents:
            s += content
            cumulative.append(s / total)

        # 计算目标累积概率
        target_cdfs = [i / n for i in range(1, n)]

        # 找到划分点
        division_points = []
        for cdf in target_cdfs:
            # 找到最小的j，使得cumulative[j] >= cdf
            j = next(j for j, val in enumerate(cumulative) if val >= cdf)
            # 线性插值
            if j == 0:
                x = bin_low_edges[0]
            else:
                frac = (cdf - cumulative[j - 1]) / (cumulative[j] - cumulative[j - 1])
                x = bin_low_edges[j] + frac * (bin_high_edges[j] - bin_low_edges[j])
            division_points.append(x)

        # 输出n个区间
        intervals = []
        current_low = bin_low_edges[0]
        for point in division_points:
            intervals.append((current_low, point))
            current_low = point
        intervals.append((current_low, bin_high_edges[-1]))

    # 输出区间
    for i, (low, high) in enumerate(intervals, 1):
        print(f"区间 {i}: 低边界 = {low}, 高边界 = {high}")
    
    # inFile = ROOT.TFile(inputFile)
    # thn = inFile.Get("hf-task-flow-charm-hadrons/hSparseFlowCharm")
    
    # fdDistr = thn.Projection(bdt_sig)
    # fdDistr.SetDirectory(0)
    
    # candidateNum = {}
    
    # do_balance = True
    # run = 0
    # while do_balance:
    #     for iCut in range(nCutSets):
    #         candidateNum[iCut] = 0
    #         for iBin in range(1, fdDistr.GetNbinsX() + 1):
    #             if cutMins[iCut] < fdDistr.GetBinCenter(iBin) and fdDistr.GetBinCenter(iBin) < cutMaxs[iCut]:
    #                 candidateNum[iCut] += fdDistr.GetBinContent(iBin)
    
    #     sorted_candidateNum = sorted(candidateNum.values())
            
    #     print("Run: " + str(run))
    #     avg_candidate_num = sum(candidateNum.values()) / len(candidateNum)
    #     for i in range(len(sorted_candidateNum) - 1):
    #         if abs(sorted_candidateNum[i+1] - sorted_candidateNum[i]) / avg_candidate_num > 0.1:
    #             do_balance = True
    #             break
    #         else:
    #             do_balance = False
        
    #     if do_balance:
    #         for dCand in candidateNum:
    #             if dCand == 0:
    #                 if candidateNum[dCand] > avg_candidate_num:
    #                     cutMaxs[0] = cutMaxs[0] - 0.01
    #                     cutMins[1] = cutMins[1] - 0.01
    #                 else:
    #                     cutMaxs[0] = cutMaxs[0] + 0.01
    #                     cutMins[1] = cutMins[1] + 0.01
    #             elif dCand == nCutSets - 1:
    #                 if candidateNum[dCand] > avg_candidate_num:
    #                     cutMaxs[nCutSets - 2] = cutMaxs[nCutSets - 2] + 0.01
    #                     cutMins[nCutSets - 1] = cutMins[nCutSets - 1] + 0.01
    #                 else:
    #                     cutMaxs[nCutSets - 2] = cutMaxs[nCutSets - 2] - 0.01
    #                     cutMins[nCutSets - 1] = cutMins[nCutSets - 1] - 0.01
    #             else:
    #                 if candidateNum[dCand] > avg_candidate_num:
    #                     cutMaxs[dCand] = cutMaxs[dCand] - 0.01
    #                     cutMins[dCand + 1] = cutMins[dCand + 1] - 0.01
    #                 else:
    #                     cutMaxs[dCand] = cutMaxs[dCand] + 0.01
    #                     cutMins[dCand + 1] = cutMins[dCand + 1] + 0.01
    #     run += 1
                
    # print("Cut sets:")
    # print(cutMins)
    # print(cutMaxs)
        
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arguments")
    parser.add_argument("inputFile", metavar="text",
                        default="an_res.root", help="input ROOT file")
    args = parser.parse_args()

    main(
        inputFile=args.inputFile
    )
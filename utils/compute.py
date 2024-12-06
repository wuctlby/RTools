import ROOT

def compute_ratio_histo(inputHistos):
    '''
    Compute the ratio histogram of the inputHistos. The fitst histogram is the denominator.

    Input:
        -inputHistos:
            list of input histograms

    Output:
        -ratio histogram
    '''
    ratioHistos = []

    for i in range(1, len(inputHistos)):
        ratioHistos.append(inputHistos[0].Clone())
        ratioHistos[-1].SetDirectory(0)
        ratioHistos[-1].Reset()
        ratioHistos[-1].SetTitle("")
        ratioHistos[-1].Add(inputHistos[i])
        ratioHistos[-1].Divide(inputHistos[0])

    return ratioHistos
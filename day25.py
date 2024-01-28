#!/usr/bin/env python3

"""
Advent of Code 2023, day 25: Snowverload

Graph min-cut.

I took another easy way out on this one.
I just output the graph in graphviz format, then visually noted
which three edges connected the two dense subgraphs.

Ed Karrels, ed.karrels@gmail.com, January 2024
"""

import sys, collections, random


"""
There are around 1500 points, each connected to at least 4 different points,
and there are three edges connecting the two subgraphs.

distance from border nodes:
     28 0
     71 1
    242 2
    571 3
    576 4
     63 5

Strategies:
 - find 6 boundary nodes by looking for nodes where the set of peers in one direction
   is different from the set of peers in every other direction
 - with a connectivity of 4, log_4(1500/2) ~= 5, so most nodes are about 4 or 5 steps
   away from the other side.
"""


class Connectivity:
  def __init__(self, rules):
    # name -> peer_list
    self.nodes = {}
    
    for src, dests in rules:
      for dest in dests:
        self.add(src, dest)

  def add(self, n1, n2):
    self.addOne(n1, n2)
    self.addOne(n2, n1)

  def addOne(self, a, b):
    peers = self.nodes.get(a, None)
    if peers == None:
      peers = [b]
      self.nodes[a] = peers
    else:
      if b not in peers:
        peers.append(b)

  def remove(self, n1, n2):
    self.nodes[n1].remove(n2)
    self.nodes[n2].remove(n1)

  def removeOne(self, a, b):
    self.nodes[a].remove(b)

  def countReachable(self, start):
    # count = 1
    visited = set()
    visited.add(start)
    q = collections.deque()
    q.append(start)

    while len(q) != 0:
      node = q.popleft()
      for peer in self.nodes[node]:
        if peer not in visited:
          visited.add(peer)
          q.append(peer)

    return len(visited)

  def shortestPath(self, src, dest):
    """
    Return the shortest path between src and dest as a list of the nodes traversed.
    """
    # node -> prev
    prev = {}

    # do a BFS seach
    # if the edges were weighted then this would use Dijkstra's algorithm
    q = collections.deque()
    q.append(src)

    # print(f'shortest path {src} -> {dest}')
    found = False
    while not found:
      node = q.popleft()
      for peer in self.nodes[node]:
        if peer not in prev:
          prev[peer] = node
          if peer == dest:
            found = True
            break
          q.append(peer)

    # walk backwards through peer links
    node = prev[dest]
    links = []
    while node != src:
      links.append(node)
      node = prev[node]

    links.reverse()
    return links
  

  def write(self, filename):
    with open(filename, 'w') as outf:
      outf.write('graph day25 {\n')
      for src, dests in self.nodes.items():
        for dest in dests:
          if src < dest:
            outf.write(f'  {src} -- {dest}\n')
      outf.write('}\n')
    print(f'wrote {filename}')
    print(f'  neato -Tpdf -oday25.pdf {filename}')


def readInput(inf):
  """
  Returns [(name, [list of names]), ...]
  """
  rules = []
  for line in inf:
    colon = line.index(':')
    src = line[:colon]
    dests = line[colon+1:].split()
    rules.append((src, dests))
  return rules

  
def part1(args):
  
  if len(args) < 1:
    print("""
  day25.py input foo-bar foo bar write:filename.gv
    Each x-y argument is a connection to be severed.
    Args which are node names start a reachability traversal.
    For each write arg write a graphviz file.
""")
    return
  

  with open(args[0]) as inf:
    con = Connectivity(readInput(inf))

  for arg in args[1:]:
    if arg.startswith('write:'):
      filename = arg[6:]
      con.write(filename)
      continue
    
    hyphen = arg.find('-')
    if hyphen != -1:
      n1,n2 = arg.split('-')
      # print(f'sever {n1} -- {n2}')
      con.remove(n1, n2)
      continue
    
    count = con.countReachable(arg)
    print(f'{count} reachable from {arg}')


# ./day25.py < day25.in.txt jpn vgf jpn-vgf nmz-mnl fdb-txm jpn vgf write:day25.cut3.gv


set1 = set_jpn = frozenset({'ljj', 'lkx', 'lqh', 'ktj', 'rqx', 'jtp',
                            'fgr', 'tcn', 'rkf', 'kcd', 'sjg', 'pfr', 'ghl', 'tkx', 'djg', 'jts',
                            'dlt', 'vnk', 'mqx', 'kng', 'vtf', 'pbc', 'hcp', 'jdx', 'ggv', 'nqx',
                            'dcp', 'qml', 'krk', 'ddq', 'bjr', 'tcq', 'fdl', 'nvp', 'hlt', 'qnq',
                            'kfc', 'btd', 'xht', 'xgl', 'nsc', 'gtg', 'ktt', 'qbh', 'dtp', 'qxf',
                            'dkg', 'frz', 'rrn', 'sck', 'shq', 'ptc', 'bld', 'crh', 'hvl', 'dkz',
                            'slb', 'hqm', 'dcb', 'pgt', 'czt', 'hcd', 'jfg', 'jjm', 'jgr', 'gbg',
                            'xrk', 'qns', 'xmf', 'jth', 'bjf', 'kxt', 'btm', 'mhx', 'hct', 'jzk',
                            'bkk', 'zll', 'lps', 'kln', 'cnt', 'xcm', 'rrp', 'dgf', 'gzk', 'pps',
                            'mdq', 'jlb', 'qkl', 'vgp', 'czv', 'mkc', 'ppq', 'gcx', 'tgk', 'lxc',
                            'kxz', 'trr', 'zzg', 'mfx', 'ssv', 'xhv', 'nmh', 'qhz', 'qmp', 'tqh',
                            'lcx', 'dss', 'vcs', 'hbn', 'jcg', 'grs', 'jgc', 'jkk', 'nnl', 'brx',
                            'png', 'rlm', 'ndp', 'rsf', 'qxd', 'jlh', 'pmz', 'zss', 'nvr', 'tmq',
                            'hgv', 'vld', 'lrk', 'mqm', 'gzr', 'fcp', 'zdf', 'vhh', 'qcl', 'rph',
                            'dmm', 'mvb', 'qmx', 'xgc', 'djz', 'rtx', 'rmz', 'zzd', 'btp', 'mvm',
                            'nxr', 'rpg', 'zsb', 'gjt', 'khj', 'rht', 'njj', 'gct', 'ggr', 'llq',
                            'lvs', 'pql', 'kcz', 'hpb', 'gvs', 'mpr', 'vsk', 'xjd', 'jnt', 'qnv',
                            'hmp', 'hbr', 'qnl', 'zjr', 'rxt', 'fgp', 'qvh', 'vtt', 'stq', 'rhk',
                            'nlv', 'qfj', 'ckg', 'kfp', 'cpk', 'drk', 'jld', 'ccp', 'tvk', 'xvq',
                            'pxm', 'gbr', 'mlj', 'bhj', 'rtg', 'rrk', 'kgh', 'lcb', 'nln', 'qcc',
                            'zhl', 'pxd', 'zhz', 'mql', 'pph', 'bxj', 'jkl', 'fts', 'sss', 'gqm',
                            'nkl', 'qbf', 'ktn', 'ggs', 'ghr', 'rrm', 'kzj', 'xrh', 'bqq', 'zlt',
                            'mxk', 'jvr', 'nxt', 'zxb', 'lbq', 'psm', 'vcr', 'klb', 'hzj', 'gtt',
                            'vfp', 'lsp', 'hbf', 'mks', 'glf', 'dzs', 'xgr', 'bln', 'fqx', 'fzv',
                            'qsc', 'vgt', 'jbc', 'jbt', 'svj', 'gtm', 'fsd', 'zxt', 'sfz', 'rmh',
                            'kqm', 'hln', 'jhm', 'fjc', 'mts', 'sqr', 'hvs', 'dzf', 'sgt', 'lbm',
                            'csn', 'bpr', 'njm', 'gjs', 'rzz', 'lcj', 'zfz', 'vgc', 'ksf', 'kpn',
                            'ppv', 'mpn', 'pmj', 'znh', 'zrd', 'ctp', 'rlk', 'qzt', 'sgm', 'svs',
                            'rcs', 'ddz', 'bfh', 'nxk', 'pff', 'qtl', 'jqn', 'dgd', 'trh', 'scm',
                            'srq', 'lkh', 'mrh', 'xfg', 'pdz', 'ppg', 'pkc', 'nrn', 'hmh', 'rpr',
                            'jhr', 'rzp', 'pkn', 'trq', 'fgx', 'dnm', 'spt', 'qgd', 'fbc', 'ksm',
                            'jvd', 'ttl', 'jmt', 'zjt', 'qjj', 'tlb', 'zkx', 'hjb', 'zgr', 'vtg',
                            'dlj', 'xrb', 'lxd', 'tff', 'vzp', 'dsr', 'frl', 'dxl', 'xdf', 'hhv',
                            'smd', 'qfx', 'srg', 'mhk', 'ffn', 'lfg', 'tjx', 'xsp', 'rsg', 'dqb',
                            'hjn', 'rdr', 'rlp', 'qsp', 'kdz', 'hrs', 'pbl', 'dgv', 'bgd', 'nsd',
                            'nnv', 'rgj', 'fjm', 'cbb', 'lms', 'pjx', 'phh', 'bbt', 'kzs', 'gqd',
                            'zct', 'fgg', 'crk', 'rbb', 'brn', 'vxl', 'qrq', 'vsq', 'fkn', 'jkf',
                            'jmm', 'csd', 'cdc', 'msg', 'hps', 'kvx', 'ksg', 'xcl', 'plz', 'gcb',
                            'tjg', 'lbl', 'hdv', 'xjh', 'qlh', 'rks', 'hfp', 'dpm', 'mmd', 'zrp',
                            'bgz', 'nds', 'fxc', 'hbb', 'mvl', 'qdm', 'hrg', 'zln', 'rxd', 'dzq',
                            'cgq', 'hnh', 'sjh', 'kvl', 'mqp', 'rpm', 'zkq', 'mfv', 'xrc', 'dmr',
                            'hsn', 'lzf', 'hdz', 'jxb', 'fdx', 'tkd', 'sxg', 'jlm', 'rjt', 'bct',
                            'xzs', 'tfs', 'ltq', 'gtr', 'dxn', 'lnr', 'nhx', 'fpm', 'vbs', 'lmh',
                            'jdn', 'zmt', 'mkp', 'lsr', 'snd', 'dtr', 'nhv', 'rgg', 'mmx', 'fcj',
                            'phj', 'vjh', 'hhz', 'srk', 'gsv', 'lcl', 'sbc', 'ntv', 'txm', 'hds',
                            'nqq', 'xmp', 'vss', 'ltp', 'bxb', 'zhg', 'rds', 'lmv', 'tgp', 'mct',
                            'vbv', 'gtp', 'ntb', 'ntt', 'tcx', 'qrd', 'qls', 'xqm', 'rnt', 'jvx',
                            'lml', 'xnb', 'vpg', 'nvj', 'zbx', 'rfv', 'mrg', 'fjr', 'xhq', 'mqg',
                            'srx', 'hlj', 'jvj', 'htc', 'cpg', 'zzm', 'clm', 'cgv', 'jkv', 'nfd',
                            'mdd', 'mzl', 'sdb', 'ndd', 'sqp', 'mvg', 'czj', 'pcr', 'zjh', 'ngg',
                            'dtd', 'ckz', 'htt', 'hjc', 'xsb', 'jch', 'ffk', 'rqp', 'jxx', 'mxt',
                            'sxx', 'tpm', 'rqr', 'qlp', 'fcv', 'kfd', 'rhj', 'krh', 'sld', 'qsf',
                            'sjc', 'thg', 'ngt', 'kkp', 'qxn', 'nxd', 'vcb', 'qlz', 'cdd', 'mgk',
                            'lqn', 'dmp', 'smz', 'nhn', 'msx', 'dbj', 'rxz', 'fbf', 'czn', 'hth',
                            'vrj', 'rdh', 'ktq', 'hkp', 'ngs', 'kbc', 'tql', 'qhc', 'shr', 'lfv',
                            'dln', 'lxl', 'cdx', 'rmg', 'kbh', 'fln', 'skp', 'vsz', 'kbp', 'vkp',
                            'tkk', 'kdc', 'dtj', 'qbj', 'fhf', 'vlf', 'mnt', 'qdk', 'zlf', 'cxx',
                            'xlv', 'cnc', 'jvk', 'shd', 'npm', 'fsn', 'gll', 'vbq', 'nrd', 'vbm',
                            'kqn', 'cgx', 'vvq', 'jdp', 'pbx', 'vbx', 'tsx', 'bjl', 'pnm', 'tsl',
                            'rss', 'zhh', 'vtz', 'chv', 'pfd', 'pgj', 'cbm', 'vsl', 'ssb', 'hpc',
                            'bpz', 'bjp', 'bkr', 'fqf', 'fqv', 'mln', 'bls', 'clh', 'vqj', 'lhc',
                            'gkn', 'pnq', 'zbq', 'qbx', 'zfc', 'zxf', 'jhp', 'vnb', 'rhv', 'rtn',
                            'jtb', 'vqg', 'vkj', 'rfq', 'gvp', 'sqt', 'qmk', 'rxv', 'lmz', 'stx',
                            'mdv', 'smx', 'dbl', 'hgs', 'ggj', 'hmm', 'rrv', 'qmj', 'lkj', 'hcs',
                            'bcd', 'hsx', 'tcp', 'fxs', 'rqb', 'pqs', 'mbh', 'zjl', 'dgq', 'ltr',
                            'fvz', 'hpn', 'bbz', 'zrj', 'bdv', 'mzm', 'dml', 'gpq', 'qjb', 'shx',
                            'ppf', 'qtp', 'pll', 'hmc', 'mlp', 'tct', 'fbt', 'bsf', 'cbx', 'lgc',
                            'jgn', 'vvd', 'mqj', 'qjs', 'bvs', 'qlb', 'bfk', 'mmg', 'nsr', 'scg',
                            'vhn', 'tfz', 'xhs', 'dpr', 'bkg', 'jnf', 'sjb', 'dqf', 'bpv', 'gfx',
                            'dtx', 'sml', 'qxk', 'kzz', 'jpn', 'mmr', 'qtt', 'mbd', 'qbv', 'htj',
                            'jzn', 'vhp', 'svr', 'bzv', 'xjg', 'vcc', 'bhn', 'bvd', 'xck', 'lnt',
                            'rpc', 'cgc', 'ksl', 'htx', 'xnq', 'mgp', 'jfm', 'ztv', 'hff', 'fsl',
                            'nnn', 'bzf', 'nhb', 'krj', 'hvh', 'hxf', 'bgf', 'vdx', 'nbf', 'kgr',
                            'hkn', 'fqs', 'kqs', 'ljk', 'pqk', 'vdc', 'tkj', 'cvr', 'bsj', 'xjx',
                            'lrp', 'zrr', 'ztc', 'xxh', 'mkg', 'rcf', 'pbg', 'pxn', 'mcc', 'scl',
                            'dck', 'vnx', 'rtm', 'pnr', 'nhl', 'cnb', 'sxb', 'dtn', 'fgz', 'zkm',
                            'tzf', 'ztl', 'dpv', 'tkz', 'chx', 'lhd', 'mnl', 'xhl', 'mdn', 'bzh'})

set2 = set_vgf = frozenset({'vvr', 'vxk', 'kzk', 'khz', 'hjp', 'kjj',
                            'xcf', 'dhc', 'kls', 'sbr', 'xvj', 'sst', 'hpt', 'xbq', 'rnk', 'fjt',
                            'jgf', 'tmp', 'spm', 'blm', 'jfp', 'txg', 'nfc', 'vpx', 'djq', 'zrm',
                            'dzn', 'snq', 'rvl', 'bmd', 'ptq', 'hjq', 'nsk', 'dxm', 'dzx', 'bvg',
                            'bqp', 'xsv', 'hlx', 'hnt', 'djr', 'rrr', 'xfd', 'qbm', 'zxn', 'jfq',
                            'btq', 'sch', 'zcg', 'pkj', 'svq', 'vqd', 'xvs', 'mpt', 'pzn', 'prb',
                            'vlt', 'srb', 'mjs', 'vpz', 'npr', 'jpx', 'jsn', 'khk', 'zsk', 'lrv',
                            'tzd', 'kbk', 'kxs', 'qvf', 'cpc', 'nfm', 'dqn', 'gjd', 'vzf', 'ccx',
                            'cjb', 'mfc', 'jjj', 'kqx', 'hgn', 'kns', 'dqk', 'ltb', 'vmp', 'sts',
                            'bzz', 'htd', 'mnb', 'mpf', 'xrj', 'vdh', 'kkj', 'lpt', 'mjb', 'hzs',
                            'xmm', 'szv', 'jdq', 'lkd', 'flk', 'qsn', 'hbv', 'ggp', 'mls', 'dqx',
                            'rmq', 'dbn', 'rff', 'pbz', 'mqr', 'hjg', 'tpq', 'kjc', 'gdp', 'lvv',
                            'mth', 'nsh', 'xpk', 'jjb', 'ppr', 'bnq', 'vtq', 'jvv', 'djj', 'fnj',
                            'cpt', 'gcr', 'zkn', 'lqx', 'hbz', 'lsk', 'jnv', 'vln', 'vrc', 'zqt',
                            'jqp', 'bch', 'lrz', 'jkc', 'hvv', 'cgr', 'bhd', 'gfb', 'jbq', 'tvj',
                            'pht', 'qvm', 'csm', 'bzn', 'jkg', 'szn', 'nxl', 'cfj', 'xps', 'bzs',
                            'qfn', 'zkt', 'kbn', 'cfh', 'dvs', 'bvb', 'fml', 'rcb', 'xgq', 'mpz',
                            'bmh', 'rnf', 'tqj', 'zzt', 'gsm', 'jzz', 'mfh', 'dgl', 'qgv', 'qrr',
                            'pzd', 'fbh', 'jqt', 'rng', 'fmj', 'qgm', 'sfv', 'pch', 'xmk', 'nvn',
                            'xgk', 'prz', 'lzc', 'lgv', 'jnz', 'hjz', 'kgc', 'qxv', 'rdq', 'vlh',
                            'tbn', 'mxr', 'djf', 'gqb', 'scx', 'htr', 'dnp', 'rrf', 'lll', 'zdt',
                            'lmb', 'rqm', 'gsl', 'jzl', 'xlh', 'rdj', 'xbd', 'gvb', 'kkt', 'jrt',
                            'xhg', 'hcf', 'vzv', 'fqj', 'bsh', 'pcg', 'gzf', 'fhr', 'bxl', 'mrb',
                            'szx', 'drj', 'gln', 'fzn', 'dvl', 'slg', 'gps', 'qgq', 'ttq', 'jfs',
                            'rjs', 'hbk', 'jxs', 'bpf', 'lpv', 'flj', 'jms', 'hdd', 'cmb', 'pgl',
                            'jbp', 'dbd', 'zzs', 'mbx', 'tvm', 'mhr', 'kdr', 'txz', 'tgn', 'psz',
                            'kbb', 'jgx', 'qdf', 'hrb', 'srj', 'lnp', 'vgl', 'cdh', 'zbb', 'tfk',
                            'vqp', 'tzj', 'vrg', 'fqg', 'sxd', 'cff', 'hxs', 'pjb', 'gmc', 'zlb',
                            'njz', 'nmc', 'msv', 'xqh', 'fjl', 'mgv', 'ssd', 'cvl', 'ccl', 'tst',
                            'jqj', 'lpl', 'lfk', 'lls', 'bpb', 'tqz', 'sfb', 'rkp', 'nbh', 'pjn',
                            'qvz', 'xzc', 'ssn', 'rcj', 'tnf', 'pkd', 'dkp', 'qds', 'dtk', 'tzm',
                            'bjz', 'vsd', 'vnm', 'hhs', 'vnp', 'zfq', 'nfk', 'mpg', 'cqp', 'tbj',
                            'mqc', 'hxp', 'qnh', 'fhd', 'dxv', 'kpv', 'mmt', 'jcz', 'bbv', 'lkv',
                            'fht', 'szz', 'jkd', 'spq', 'tbs', 'mpm', 'zlq', 'nfz', 'tjt', 'stv',
                            'zzn', 'frd', 'lcp', 'gzt', 'vjz', 'xph', 'tgt', 'hlk', 'jjr', 'cvz',
                            'ktm', 'nlx', 'qvn', 'mdp', 'gzn', 'mrt', 'vqh', 'zxr', 'grl', 'clp',
                            'fdb', 'mdh', 'ntj', 'xls', 'ljs', 'plm', 'frk', 'npq', 'jxl', 'grx',
                            'bvv', 'klr', 'lvm', 'lnm', 'dms', 'fnz', 'bxf', 'cxf', 'bxq', 'bbg',
                            'khn', 'lmf', 'xhm', 'brh', 'xqc', 'pgz', 'clt', 'xsf', 'ctk', 'gtl',
                            'rkq', 'nzk', 'vsj', 'fvp', 'bjj', 'cdm', 'mpp', 'crg', 'kjm', 'njk',
                            'jpp', 'jcv', 'mvc', 'vqq', 'kvd', 'jrr', 'xgh', 'tdh', 'shm', 'ptg',
                            'gvd', 'jft', 'mxh', 'cfl', 'rxk', 'grh', 'nvs', 'rsm', 'vmj', 'sgn',
                            'jmd', 'fng', 'jdz', 'qvc', 'gdc', 'sgx', 'hng', 'rkm', 'fvl', 'gcs',
                            'tsn', 'tks', 'zcr', 'bdq', 'clj', 'bcs', 'hjj', 'hnn', 'zpt', 'xlm',
                            'kkn', 'jpb', 'xqg', 'pnp', 'tkf', 'qpv', 'bzm', 'gxh', 'fvc', 'cqh',
                            'rvc', 'xdn', 'bpd', 'jpd', 'npd', 'lzg', 'gjc', 'rnq', 'jcm', 'pth',
                            'tqt', 'bkf', 'bnx', 'bbq', 'dkk', 'khx', 'nkd', 'gpf', 'kjg', 'vts',
                            'qph', 'zck', 'gdm', 'tfd', 'sfk', 'lvp', 'xlc', 'vcq', 'ldm', 'hqn',
                            'dpl', 'xlx', 'ldb', 'bst', 'sgj', 'xmj', 'jlt', 'xpg', 'klk', 'sbq',
                            'dbp', 'srz', 'gbm', 'xct', 'prn', 'crx', 'smh', 'njs', 'tjf', 'hvr',
                            'crq', 'lnc', 'ljq', 'dgz', 'bnd', 'lmd', 'gsc', 'shc', 'jxr', 'pln',
                            'rpk', 'knr', 'vkm', 'qbq', 'sxc', 'lkp', 'rcm', 'mrd', 'sfl', 'zdz',
                            'pgg', 'sff', 'qdc', 'fqq', 'qbp', 'vcm', 'pdj', 'pzc', 'prc', 'zng',
                            'rcx', 'qrg', 'kgs', 'fzq', 'jzv', 'cls', 'pjc', 'zlv', 'ccr', 'kps',
                            'mlq', 'xcj', 'hml', 'lvz', 'rbf', 'zjg', 'gvc', 'bnt', 'tmb', 'zgb',
                            'dps', 'xxc', 'lbj', 'hbh', 'bgx', 'txt', 'khs', 'nqz', 'cjp', 'qnx',
                            'gcd', 'cjk', 'vrh', 'vsh', 'ckk', 'rvt', 'zzq', 'qkd', 'llm', 'xfn',
                            'qgc', 'vnf', 'czp', 'gqt', 'sbn', 'drp', 'qqr', 'xlf', 'btt', 'gmh',
                            'mft', 'gfn', 'bqh', 'nts', 'lzk', 'bpm', 'fnh', 'sms', 'kmd', 'nrv',
                            'tvq', 'dcv', 'lrq', 'tms', 'rjl', 'hch', 'ljt', 'dpq', 'ngn', 'bdj',
                            'gsq', 'jmp', 'lmg', 'mvr', 'qss', 'ncl', 'dfz', 'gdt', 'bsg', 'mfs',
                            'vxb', 'hkf', 'tcf', 'dnv', 'bss', 'qgt', 'jxz', 'xlk', 'hlm', 'dsh',
                            'hfr', 'vlx', 'cmh', 'vjc', 'xfq', 'djp', 'ggb', 'xgv', 'jqk', 'hxq',
                            'tdp', 'rvp', 'mjx', 'hcv', 'pbs', 'fnv', 'xzd', 'nbb', 'rpp', 'snc',
                            'lhx', 'rqq', 'zls', 'lpb', 'mhf', 'gls', 'ftm', 'pkv', 'vxt', 'bbk',
                            'fxg', 'vpl', 'gft', 'srs', 'kzt', 'zsf', 'clf', 'chz', 'rmp', 'lrh',
                            'nch', 'ljv', 'lgp', 'zps', 'cgd', 'cxp', 'dsm', 'tnj', 'fdv', 'kmr',
                            'ftc', 'drv', 'qpk', 'qvb', 'ksk', 'phd', 'gkk', 'bvp', 'tft', 'vvk',
                            'kdv', 'pmh', 'jpf', 'crj', 'mhl', 'sjz', 'fbr', 'drg', 'ltm', 'dqg',
                            'tjp', 'zhd', 'vdf', 'htq', 'phg', 'vxs', 'dpd', 'zch', 'xgf', 'sct',
                            'fkm', 'jps', 'sgb', 'pbr', 'jlk', 'frh', 'skb', 'qcp', 'qmg', 'rcv',
                            'rtk', 'ssg', 'fxn', 'dhg', 'nfj', 'ckm', 'hnd', 'zxc', 'fks', 'dsk',
                            'xpn', 'jjq', 'qhh', 'sxn', 'hqg', 'dvq', 'rvd', 'pjt', 'smb', 'rnd',
                            'nnq', 'vlq', 'jjs', 'hdf', 'krn', 'zgv', 'fpg', 'grb', 'hpf', 'npz',
                            'tht', 'mjj', 'jdl', 'pnc', 'mpb', 'msf', 'vxp', 'mjh', 'gxk', 'fsm',
                            'qzd', 'ldd', 'czz', 'zdd', 'tvl', 'jpc', 'pcb', 'gxv', 'nmz', 'lnb',
                            'vgf', 'dtv', 'jjc', 'chc', 'qsk', 'dsd', 'rjb', 'gmt', 'tfl', 'sht',
                            'rbk', 'xrg', 'cpd', 'hnv', 'gmz', 'xxm', 'kms', 'mvs', 'trl', 'lvd',
                            'nlc', 'nkz', 'fbl', 'bqg', 'fpr', 'dvj', 'lch', 'rvb', 'cvn'})

set_lookup = {}
for x in set1: set_lookup[x] = 1
for x in set2: set_lookup[x] = 2


def distanceFromBorderNode(graph, origin, border_nodes = None):
  if not border_nodes:
    border_nodes = set(['jpn', 'vgf', 'nmz', 'mnl', 'fdb', 'txm'])

  visited = set()
  q = collections.deque()
  q.append((origin, 0))

  while True:
    (node, dist) = q.popleft()
    visited.add(node)
    for peer in graph.nodes[node]:
      if peer in border_nodes:
        return dist
      elif peer not in visited:
        q.append((peer, dist+1))


def reachableSet(graph, origin):
  visited = set()
  q = collections.deque()
  q.append(origin)

  while q:
    node = q.popleft()
    visited.add(node)
    for peer in graph.nodes[node]:
      if peer not in visited:
        q.append(peer)

  return visited
  

def outputHalves(graph):
  border_nodes = frozenset(['jpn', 'vgf', 'nmz', 'mnl', 'fdb', 'txm'])
  graph.remove('jpn', 'vgf')
  graph.remove('nmz', 'mnl')
  graph.remove('fdb', 'txm')

  set1 = reachableSet(graph, 'jpn')
  set2 = reachableSet(graph, 'vgf')
  print(f'set1 = set_jpn = frozenset({set1!r})')
  print(f'set2 = set_vgf = frozenset({set2!r})')


def crossoverFrequency(graph):
  """
  number of steps between switching sides
  0       0       101
  10      1       100
  20      1       100
  30      11.6    100
  40      270.6   100
  50      519.5   100
  60      854     100
  70      1309    100
  80      2001    100
  90      3121    101
  100     1.481e+04

  Median number of steps is 519.

  """
  # choose random starting node
  node = random.choice(list(graph.nodes.keys()))

  steps = 0
  print(f'start at {node!r}')
  side = set_lookup[node]
  print(f'{steps} side {side}')
  flop_count = 0
  prev_flop = 0
  while True:
    # print(f'graph.nodes[node] = {graph.nodes[node]}')
    node = random.choice(graph.nodes[node])
    steps += 1
    next_side = set_lookup[node]
    if next_side != side:
      side = next_side
      # print(f'{steps} side {side} {node}')
      print(str(steps - prev_flop))
      prev_flop = steps
      flop_count += 1
      if flop_count == 1000:
        break


def commonEdges(graph, count = 200):
  """
  Choose N random pairs of points, and find the shortest path between them.
  For each edges along each of those paths, increment a counter.
  This tracks the most common edges.
  Since just three edges connect the two halves of the graph, they
  should be traversed most often in this test.
  For the given inputs of around 1500, I found 200 iterations
  sufficient to distinguish the three edges.
  """
  all_nodes = list(graph.nodes.keys())

  pairs_tested = set()
  edges_seen = collections.Counter()

  def orderedTuple(a, b):
    # make a key out of a pair by ordering them and putting them in a tuple
    if a < b:
      return (a, b)
    else:
      return (b, a)

  for test_count in range(count):
    test_pair = orderedTuple(*random.sample(all_nodes, 2))
    test_pair = tuple(test_pair)
    if test_pair in pairs_tested:
      # don't test the same pair twice
      continue
    path = graph.shortestPath(*test_pair)
    # print(f'{test_pair}: {path}')

    # add all edges of the path to edges_seen
    src, dest = test_pair
    edges = []
    if len(path) == 0:
      edges.append(orderedTuple(src, dest))
    else:
      edges.append(orderedTuple(src, path[0]))
      for i in range(1, len(path)):
        edges.append(orderedTuple(path[i-1], path[i]))
      edges.append(orderedTuple(path[-1], dest))
    edges_seen.update(edges)

    # print(repr(edges_seen))

  edges_by_freq = [(value,key) for key,value in edges_seen.items()]
  edges_by_freq.sort(reverse=True)
  """
  print(f'after {test_count+1} tests')
  for freq, edge in edges_by_freq[:6]:
    print(f'  {freq} {edge}')
  """
  return [x[1] for x in edges_by_freq[:3]]
  

  
def analyze(filename):
  with open(filename) as inf:
    graph = Connectivity(readInput(inf))

  # see the range of adjacent count
  # range is 4..9 with a median of 4
  # counts = [len(peers) for peers in con.nodes.values()]
  # counts.sort()
  # print(f'{len(counts)} counts {counts[0]}..{counts[len(counts)//2]}..{counts[-1]}')

  # border_nodes = frozenset(['jpn', 'vgf', 'nmz', 'mnl', 'fdb', 'txm'])
  # for node in graph.nodes.keys():
  #   dist = distanceFromBorderNode(graph, node)
  #   print(f'{dist} {node}')

  # outputHalves(graph)

  # crossoverFrequency(graph)

  common_edges = commonEdges(graph)
  n1,n2 = common_edges[0]
  for a,b  in common_edges:
    graph.remove(a, b)

  size1 = graph.countReachable(n1)
  size2 = graph.countReachable(n2)
  # print(f'from {n1} {size1} reachable')
  # print(f'from {n2} {size2} reachable')
  print(f'part2 {size1 * size2}')


if __name__ == '__main__':
  args = sys.argv[1:]
  if len(args) == 0:
    args = ["day25.in.txt", 'jpn-vgf', 'nmz-mnl', 'fdb-txm', 'jpn', 'vgf']

  # part1(args)
  analyze(args[0])
  

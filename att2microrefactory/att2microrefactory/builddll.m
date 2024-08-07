function builddll(target)
%build mex or build lib


    entryPoint = 'atti2micro';


   %% Configuration for generating C++ code as a DLL
    cfg = coder.config('dll');
    cfg.TargetLang = 'C++';
    cfg.GenerateReport = true;
    cfg.LaunchReport = false;
    
    % Correct usage for CustomInclude and CustomSource with String Arrays
    cfg.CustomInclude = ["/media/sf_att2microrefactory/att2microrefactory/micro2moments"];
    cfg.CustomSource = ["threadHelper.cpp", "dmri_2F1cplus.cpp", "hyperGeom2F1.cpp", "generateSHMatrix.cpp", "sh2hot.cxx", "sphericalHarmonics.cpp"];
    
    cfg.CustomSourceCode = ['#include "generateSHMatrix.h"'];



       
    load test_data.mat;
    atti = double(atti);
    T=toc; % This is always a large piece of data
    fprintf(1,'It took %f seconds to load data\n',T);
    
    tic;
    [M,N,P,G] = size(atti);
    options = create_atti2micro_options(mask,M,N,P,G); % you need a way to pass the data and other options to the line below
    % Convert atti data to microstructure parameters using the simplest use case
   [M,N,P,G] = size(atti);
    options = create_atti2micro_options(mask,M,N,P,G); % you need a way to pass the data and other options to the line below
    
    
    %generate code
    codegen(entryPoint,'-args',{atti, gi,bi, options},'-config', cfg);
end
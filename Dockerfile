FROM continuumio/anaconda3

RUN pip install boto3 pandas scikit-learn pulp pyomo inspyred ortools scipy deap 

RUN conda install -c conda-forge ipopt coincbc glpk

ENV PYTHONUNBUFFERED=TRUE

ENTRYPOINT ["python"]